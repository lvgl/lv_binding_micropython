# all items that are not results MUST begin with an underscore
# this includes imports. This is so the test program can remove everything
# that is not a result as it is not going to be needed beyond this script.
# if there is a lot of additional code that is to be used to generate the
# results you can add additional python source files in the same folder
# as your results file and you can do an import. Remember to rename the import
# sio it begine with an underscore. If you do this DO NOT add _results to the
# filename of the additional source files.

from PIL import Image as _Image
import os as _os

FRAME = _Image.open(
    _os.path.join(_os.path.dirname(__file__), 'test_image_compare.png')
)