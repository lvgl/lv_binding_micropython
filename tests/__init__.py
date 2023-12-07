import unittest
import os
import subprocess
import threading
from typing import TYPE_CHECKING
import argparse
import signal
import traceback
from io import BytesIO
import binascii
import time
import sys

from PIL import Image
import apng


DEBUG = 0


def log(*args):
    if DEBUG:
        args = ' '.join(repr(arg) for arg in args)
        sys.stdout.write('\033[31;1m' + args + '\033[0m\n')
        sys.stdout.flush()


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
    # these are here simply to make an IDE happy. Their values get dynamically
    # set when the class gets constructed
    process: subprocess.Popen = None
    lock: threading.Lock = None
    exit_event: threading.Event = None
    test_path: str = ''

    def send(cls, cmd):
        if cls.process is None:
            return
        log('<---', cmd)
        cls.process.stdin.write(cmd)
        cls.process.stdin.flush()

    def read_until(cls, marker):
        micropy_data = b''

        log('MARKER', marker)

        logged = False

        while not micropy_data.endswith(marker) and not cls.exit_event.is_set():
            char = cls.process.stdout.read(1)
            if char:
                micropy_data += char
                logged = False
            else:
                logged = True
                log('--->', micropy_data)

        if not logged:
            log('--->', micropy_data)

        if cls.exit_event.is_set():
            log('*** EXIT EVENT SET ***')

        return micropy_data.replace(marker, b'')

    def setUpClass(cls):
        os.chdir(cls.test_path)
        log(f'--SETTING UP {cls.__name__}')
        cls.process = subprocess.Popen(
            ['bash'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=os.environ,
            shell=True,
            preexec_fn=os.setsid
        )
        log(f'--RUNNING MICROPYTHON ({MICROPYTHON_PATH})')

        cls.send(b'cd ' + cls.test_path.encode('utf-8') + b'\n')
        cls.send(MICROPYTHON_PATH.encode('utf-8') + b'\n')
        cls.read_until(b'>>>')

        log('--MICROPYTHON STARTED')

    def tearDownClass(cls):
        log('--TEARDOWN STARTED')

        if cls.process is not None:
            cls.send(CTRL_C)
            cls.send(CTRL_C)
            cls.send(CTRL_D)

            if not cls.process.stdin.closed:
                cls.process.stdin.close()

            os.killpg(os.getpgid(cls.process.pid), signal.SIGTERM)

            cls.process.wait()

            if not cls.process.stdout.closed:
                cls.process.stdout.close()

            if not cls.process.stderr.closed:
                cls.process.stderr.close()

            cls.process = None

        log(f'--TEARDOWN FINISHED')

    def run_test(self, settings: dict, code) -> TestData:
        self.__class__.lock.acquire()
        timeout = settings.get('TIMEOUT', 500)
        test_type = settings.get('TEST_TYPE', None)
        wait = settings.get('WAIT', 0)

        code = code.strip()

        if self.__class__.process is None:
            self.__class__.lock.release()
            return False

        if not code.endswith(b'\r\n# end'):
            self.__class__.lock.release()
            self.fail('Last line of test code is not "# end"')

        self.send(CTRL_E)
        self.read_until(PASTE_PROMPT)

        code = code.split(b'\r\n')

        for i, line in enumerate(code):
            self.send(line + b'\n')
            self.read_until(b'\n')

            time.sleep(0.002)

        # self.read_until(b'# end\n')

        def _do(td: TestData):
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
                        lne = self.read_until(b'\n')

                        while lne != b'FRAME END':
                            td.watchdog_timer = time.time()
                            data.append(binascii.unhexlify(lne))
                            lne = self.read_until(b'\n')
                            if self.__class__.exit_event.is_set():
                                return

                        frame = bytearray(b''.join(data))
                        frame = [[frame[j + 2], frame[j + 1], frame[j]] for j in range(0, len(frame), 3)]
                        frame = bytes(bytearray([
                            item for sublist in frame
                            for item in sublist
                        ]))

                        img = Image.new('RGB', (width, height))
                        img.frombytes(frame)
                        td.result.append(img)
                    except:  # NOQA
                        traceback.print_exc()

                        td.error_data = traceback.format_exc()

                        return

                    curr_time = time.time()
            else:
                td.result = b''
                self.read_until(PASTE_PROMPT + b' \n')

                try:
                    td.result += self.read_until(REPL_PROMPT)
                    if self.__class__.exit_event.is_set():
                        return

                    td.watchdog_timer = time.time()
                    ns = {}
                    exec(td.result, ns)

                    for key in list(ns.keys()):
                        if key.startswith('_'):
                            del ns[key]

                    td.result = ns

                except:  # NOQA
                    import traceback

                    td.error_data = traceback.format_exc()
                    return

            td.event.set()

        test_data = TestData(test_type)

        t = threading.Thread(
            target=_do,
            args=(test_data,)
        )
        t.daemon = True
        test_data.watchdog_timer = time.time()
        self.send(CTRL_D)

        test_data.event.wait(wait / 1000)
        t.start()

        while (
            (time.time() - test_data.watchdog_timer) * 1000 <= timeout and
            not test_data.event.is_set()
        ):
            test_data.event.wait(timeout / 1000)

        if not test_data.event.is_set():
            self.__class__.exit_event.set()
            t.join()

        if test_type and test_type == 'image':
            test_data.event.set()

        if self.__class__.process is not None:
            self.send(CTRL_C)
            self.send(CTRL_C)
            # self.read_until(REPL_PROMPT)

            if not test_data.event.is_set():
                self.send(CTRL_D)

                if not self.__class__.process.stdin.closed:
                    self.__class__.process.stdin.close()

                os.killpg(os.getpgid(self.__class__.process.pid), signal.SIGTERM)

                log('*** WAITING FOR PROCESS TO TERMINATE ***')
                self.__class__.process.wait()

                log('*** PROCESS TERMINATED ***')

                if not self.__class__.process.stdout.closed:
                    self.__class__.process.stdout.close()

                if not cls.process.stderr.closed:
                    self.__class__.process.stderr.close()

                self.__class__.process = None

        self.__class__.exit_event.clear()
        self.__class__.lock.release()
        return test_data


# this is a goofy thing to do but no parameteres
# can be passed to a running test. so I have to wrap the function in other
# functions to be able to pass the parameters to the test.
def test_wrapper(t_name, t_path, t_settings, t_code, t_results):
    def _wrapper1(func):
        def _wrapper2(self):
            return func(self, t_name, t_path, t_settings, t_code, t_results)

        _wrapper2.__name__ = t_name
        return _wrapper2
    return _wrapper1


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

            # this is where the class gets dynamically constructed. Each group
            # of tests has a class made and each test has a method made.
            # The method is what you see below.

            @test_wrapper(test_name, test_path, settings, test_code, test_results)
            def _run_test(
                self: TestBase,
                t_name,
                t_path,
                t_settings,
                t_code,
                t_results
            ):

                t_type = t_settings.get('TEST_TYPE', None)

                log(f'--RUNNING TEST {t_name}-{t_type} ({t_path})')

                test_data = self.run_test(t_settings, t_code)

                if test_data is False:
                    self.skipTest('MicroPython failure')

                elif test_data.error_data:
                    log(f'--TEST FAILED {t_name}-{t_type}')
                    log(test_data.error_data)

                    self.fail(test_data.error_data)

                elif t_type and t_type == 'image':
                    artifact_path = os.path.join(
                        ARTIFACT_PATH,
                        t_name + '.apng'
                    )

                    def save_apng():
                        try:
                            artifact.save(artifact_path)
                        except:
                            traceback.print_exc()

                    artifact = apng.APNG()



                    if 'FRAME' in t_results:
                        comp_data = list(t_results['FRAME'].getdata())
                        passed = False
                    else:
                        comp_data = None
                        passed = True

                    for frame_num, img in enumerate(test_data.result):
                        byte_data = list(img.getdata())
                        writer = BytesIO()
                        img.save(writer, 'PNG')
                        writer.seek(0)
                        png = apng.PNG.from_bytes(writer.read())
                        artifact.append(png)

                        img.save(os.path.join(
                            ARTIFACT_PATH,
                            f'frame{frame_num}.png'
                        ), 'PNG')

                        with open(os.path.join(
                            ARTIFACT_PATH,
                            f'frame{frame_num}.bin'
                        ), 'wb') as f:
                            # have to flatten the data and remove the alpha
                            # from the PIL image it is formatted as
                            # [(a, r, g, b), (a, r, g, b)]
                            f.write(bytes(bytearray([
                                item for sublist in byte_data
                                for item in sublist[:-1]
                            ])))

                        if comp_data is None and f'FRAME{frame_num}' in t_results:
                            save_apng()
                            f_data = list(t_results[f'FRAME{frame_num}'].getdata())
                            if passed and f_data != byte_data:
                                passed = False

                        elif comp_data is not None:
                            if comp_data == byte_data:
                                passed = True
                        else:
                            print(
                                f'Missing frame {frame_num} '
                                f'data in results file.'
                            )

                    save_apng()
                    self.assertTrue(
                        passed,
                        f'Mismatch in captured frames ({artifact_path})'
                    )

                else:
                    log(f'--TEST DATA {t_name}-{t_type}')
                    log(f'{test_data.result}')
                    self.assertDictEqual(
                        test_data.result,
                        t_results,
                        'Result data is not equal'
                    )
            # methods are just like any other attribute. It gets sat into
            # the classes namespace which is what you have below
            namespace[test_name] = _run_test

        # add the rest of the methods and attributes
        # that are needed to the namespace
        namespace['micropy_data'] = b''
        namespace['process'] = None
        namespace['setUpClass'] = classmethod(TestBase.setUpClass)
        namespace['tearDownClass'] = classmethod(TestBase.tearDownClass)
        namespace['run_test'] = TestBase.run_test
        namespace['read_until'] = classmethod(TestBase.read_until)
        namespace['send'] = classmethod(TestBase.send)
        namespace['__name__'] = test
        namespace['lock'] = threading.Lock()
        namespace['exit_event'] = threading.Event()
        namespace['test_path'] = test_path

        # This is where the clas gets assembled. we set it into the
        # namespace at the module level so unittests will run the test
        globals()[test] = type(test, (unittest.TestCase,), namespace)


cwd = os.path.abspath(os.getcwd())

ARTIFACT_PATH = os.path.join(cwd, 'artifacts')
MICROPYTHON_PATH = os.path.join(cwd, 'micropython')


if __name__ == '__main__':
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
    arg_parser.add_argument(
        '--debug',
        dest='debug',
        help='enable debugging output',
        action='store_true'
    )

    args = arg_parser.parse_args()
    sys.argv = sys.argv[:-2]

    ARTIFACT_PATH = os.path.join(cwd, args.artifact_path)
    MICROPYTHON_PATH = os.path.join(cwd, args.mpy_path)
    DEBUG = args.debug

    if not os.path.exists(ARTIFACT_PATH):
        raise RuntimeError(f'Artifact path does not exist ({ARTIFACT_PATH})')

    if not os.path.exists(MICROPYTHON_PATH):
        raise RuntimeError(f'MicroPython binary not found ({MICROPYTHON_PATH})')

    run()
    unittest.main()
