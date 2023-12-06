import unittest
import os
import subprocess
import time
import threading
from typing import TYPE_CHECKING
import argparse

from PIL import Image
import apng
from io import BytesIO
import binascii
import time

'python3 lib/lv_bindings/tests/__init__.py --artifact-path=lib/lv_bindings/tests/artifacts --mpy-path=ports/unix/build-standard/micropython'

TEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'micropy_tests')
)

CTRL_C = b'\x03'  # 2 times to exit any running code
CTRL_D = b'\x04'  # exit paste mode committing and running what has been pasted
CTRL_E = b'\x05'  # enter paste mode

PASTE_PROMPT = b'==='
REPL_PROMPT = b'>>>'

os.environ['MICROPYINSPECT'] = '1'


class TestData:

    def __init__(self, test_type):
        self.test_type = test_type
        self.watchdog_timer = time.time()
        self.result = None
        self.error_data = ''
        self.event = threading.Event()


if TYPE_CHECKING:
    TestCase = unittest.TestCase
else:
    TestCase = object


class TestBase(TestCase):
    process: subprocess.Popen = None
    micropy_data = b''

    def read_until(cls, marker):
        micropy_data = b''

        while not micropy_data.endswith(marker):
            char = cls.process.stdout.read(1)
            if char:
                micropy_data += char

        return micropy_data.rreplace(marker, b'', 1)

    def setUpClass(cls):
        print('setup')
        cls.process = subprocess.Popen(
            ['bash'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=os.environ,
            shell=True
        )
        micropy_data = b''

        cls.process.stdin.write(MICROPYTHON_PATH.encode('utf-8') + b'\n')
        cls.process.stdin.flush()

        cls.read_until(b'>>>')

    def tearDownClass(cls):
        if cls.process is not None:
            if not cls.process.stdin.closed:
                cls.process.stdin.close()
                
            if not cls.process.stdout.closed:
                cls.process.stdout.close()

            if not cls.process.stderr.closed:
                cls.process.stderr.close()
            
            cls.process = None
    
    def run_test(self, settings: dict, code) -> TestData:
        timeout = settings.get('TIMEOUT', 500)
        test_type = settings.get('TEST_TYPE', None)
        wait = settings.get('WAIT', 0)

        if self.__class__.process is None:
            return False
        
        if not code.endswith(b'\n# end'):
            self.fail('Last line of test code is not "# end"')

        self.__class__.process.stdin.write(CTRL_E)
        self.__class__.process.stdin.flush()

        self.read_until(PASTE_PROMPT)

        for line in code.split(b'\n'):
            self.__class__.process.stdin.write(line + b'\n')
            self.__class__.process.stdin.flush()
            time.sleep(0.002)

        def _do(p, td: TestData):
            td.watchdog_timer = time.time()

            if td.test_type and td.test_type == 'image':
                width = settings['IMG_WIDTH']
                height = settings['IMG_HEIGHT']
                duration = settings['DURATION']
                curr_time = capture_start = time.time()
                td.result = []

                while (curr_time - capture_start) * 1000 <= duration:
                    try:
                        self.read_until(b'FRAME START\n')
                        data = []
                        line = self.read_until(b'\n')

                        while line != b'FRAME END':
                            td.watchdog_timer = time.time()
                            data.append(binascii.unhexlify(eval(line)))
                            line = self.read_until(b'\n')

                        frame = b''.join(data)
                        img = Image.new('RGB', (width, height))
                        img.frombytes(frame)
                        td.result.append(img)
                    except:  # NOQA
                        import traceback
                        traceback.print_exc()

                        td.error_data = traceback.format_exc()

                        return

                    curr_time = time.time()

            else:
                td.result = b''
                try:
                    p.poll()
                    d.result += self.read_until(REPL_PROMPT)
                    td.watchdog_timer = time.time()
                except:  # NOQA
                    import traceback

                    td.error_data = traceback.format_exc()
                    return

            td.event.set()

        test_data = TestData(test_type)

        t = threading.Thread(
            target=_do,
            args=(self.__class__.process, test_data)
        )
        t.daemon = True

        self.__class__.process.stdin.write(CTRL_D)
        self.__class__.process.stdin.flush()
        self.read_until(b'# end\n')

        test_data.event.wait(wait / 1000)
        td.watchdog_timer = time.time()
        t.start()

        while (
            (time.time() - test_data.watchdog_timer) * 1000 <= timeout and
            not test_data.event.is_set()
        ):
            test_data.event.wait(timeout / 1000)

        if test_data.event.is_set():
            if test_type and test_type != 'image':
                test_data.result = test_data.result[:-4].decode('utf-8')
            
                ns = {}
                try:
                    exec(test_data.result, __locals=ns)
                except:  # NOQA
                    import traceback

                    test_data.error_data = traceback.format_exc()

                test_data.result = ns

        if (
            self.__class__.process is not None and
            not self.__class__.process.poll()
        ):
            self.__class__.process.stdin.write(CTRL_C)
            self.__class__.process.stdin.write(CTRL_C)
            self.__class__.process.stdin.flush()
            self.read_until(REPL_PROMPT)

            if not test_data.event.is_set():
                self.__class__.process.stdin.write(CTRL_D)
                self.__class__.process.stdin.flush()
                self.__class__.process.stdin.close()
                self.__class__.process.kill()

                if not self.__class__.process.stdout.closed:
                    self.__class__.process.stdout.close()

                if not self.__class__.process.stderr.closed:
                    self.__class__.process.stderr.close()

                self.__class__.process = None

        return test_data
            

def test_func_wrapper(name, t_path, t_code, t_results: dict, t_settings: dict):
    def _wrapper(func):

        def _func_wrapper(self):
            func(self, name, t_path, t_settings, t_code, t_results)

        _func_wrapper.__name__ = name
        
        return _func_wrapper
    
    return _wrapper


def run():
    for test in os.listdir(TEST_PATH):
        print(f'procesing {test}')
        test_path = os.path.join(TEST_PATH, test)

        namespace = {}

        test_files = [
            file for file in os.listdir(test_path)
            if '_micropy' in file
        ]

        for file in test_files:
            test_name = os.path.splitext(file)[0][:-8]
            test_file = os.path.join(test_path, file)
            results_file = os.path.join(test_path, test_name + '_results.py')
            settings_file = os.path.join(test_path, test_name + '_settings.py')
            test_results = {'__file__': results_file}
            settings = {'__file__': settings_file}

            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    exec(f.read(), settings)

                for key in list(settings.keys()):
                    if key.startswith('_'):
                        del settings[key]

            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    dta = f.read()
                    exec(dta, test_results)

                for key in list(test_results.keys()):
                    if key.startswith('_'):
                        del test_results[key]

            with open(test_file, 'rb') as f:
                test_code = f.read()

            @test_func_wrapper(
                test_name, test_path, test_code, test_results, settings
            )
            def _run_test(
                self: TestBase,
                t_name,
                t_path,
                t_settings,
                t_code,
                t_results
            ):
                os.chdir(t_path)

                t_type = t_settings.get('TEST_TYPE', None)
                test_data = self.run_test(t_settings, t_code)

                if test_data is False:
                    self.skipTest('MicroPython failure')

                elif test_data.error_data:
                    self.fail(test_data.error_data)

                elif t_type and t_type == 'image':

                    def save_apng():
                        artifact_path = os.path.join(
                            ARTIFACT_PATH,
                            t_name + '.apng'
                        )
                        try:
                            artifact.save(artifact_path)
                        except:
                            import traceback

                            traceback.print_exc()

                    artifact = apng.APNG()

                    passed = False

                    if 'FRAME' in t_results:
                        comp_data = list(t_results[f'FRAME'].getdata())
                    else:
                        comp_data = None

                    for frame_num, img in enumerate(test_data.result):
                        byte_data = list(img.getdata())
                        writer = BytesIO()
                        img.save(writer, 'PNG')
                        writer.seek(0)
                        png = apng.PNG.from_bytes(writer)
                        artifact.append(png)

                        img.save(os.path.join(
                            ARTIFACT_PATH,
                            f'frame{frame_num}.png'
                        ), 'PNG')

                        with open(os.path.join(
                            ARTIFACT_PATH,
                            f'frame{frame_num}.bin'
                        ), 'wb') as f:
                            # have to flattem the data and remove the alpha
                            # from the PIL image it is formatted as
                            # [(r, g, b, a), (r, g, b, a)]
                            f.write(bytes(bytearray(
                                [
                                    item for sublist in byte_data
                                    for item in sublist[:-1]
                                ]
                            )))

                        if comp_data is None and f'FRAME{frame_num}' in t_results:
                            save_apng()
                            self.assertEqual(
                                list(t_results[f'FRAME{frame_num}'].getdata()),
                                byte_data,
                                'Frames do not match'
                            )
                        elif comp_data is not None:
                            if comp_data == byte_data:
                                passed = True
                        else:
                            save_apng()
                            self.fail(
                                f'Missing frame {frame_num} '
                                f'data in results file.'
                            )

                    save_apng()
                    self.assertTrue(
                        passed,
                        f'No matching frame buffer data ({artifact_path})'
                    )

                else:
                    self.assertDictEqual(
                        test_data.result,
                        t_results,
                        'Result data is not equal'
                    )

            namespace[test_name] = _run_test

        namespace['micropy_data'] = b''
        namespace['process'] = None
        namespace['setUpClass'] = classmethod(TestBase.setUpClass)
        namespace['tearDownClass'] = classmethod(TestBase.tearDownClass)
        namespace['run_test'] = TestBase.run_test
        namespace['read_until'] = classmethod(TestBase.read_until)
        namespace['__name__'] = test

        globals()[test] = type(test, (unittest.TestCase,), namespace)


cwd = os.path.abspath(os.getcwd())

ARTIFACT_PATH = os.path.join(cwd, 'artifacts')
MICROPYTHON_PATH = os.path.join(cwd, 'micropython')


if __name__ == '__main__':
    import sys

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--artifact-path',
        dest='artifact_path',
        help='path to save artifacts to',
        action='store'
    )
    arg_parser.add_argument(
        '--mpy-path',
        dest='mpy_path',
        help='path to micropython',
        action='store'
    )

    args = arg_parser.parse_args()
    sys.argv = sys.argv[:-2]

    ARTIFACT_PATH = os.path.join(cwd, args.artifact_path)
    MICROPYTHON_PATH = os.path.join(cwd, args.mpy_path)

    if not os.path.exists(ARTIFACT_PATH):
        raise RuntimeError(f'Artifact path does not exist ({ARTIFACT_PATH})')

    if not os.path.exists(MICROPYTHON_PATH):
        raise RuntimeError(f'MicroPython binary not found ({MICROPYTHON_PATH})')

    run()
    unittest.main()
