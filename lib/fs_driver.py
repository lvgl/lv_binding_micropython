'''
Original author: mhepp(https://forum.lvgl.io/u/mhepp/summary)
'''

import lvgl as lv
import uerrno
import ustruct as struct

def fs_open_cb(drv, fs_file, path, mode):
    p_mode = ''
    if mode == 1:
        p_mode = 'wb'
    elif mode == 2:
        p_mode = 'rb'
    elif mode == 3:
        p_mode = 'rb+'

    if p_mode == '':
        print("fs_open_callback() - open mode error, {} is invalid mode".format(mode))
        return lv.FS_RES.INV_PARAM

    cast_fs = lv.fs_file_t.cast(fs_file)

    try:
        f = open(path, p_mode)
        cast_fs.file_d = {'file': f}
    except Exception as e:
        print("fs_open_callback() exception: ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_close_cb(drv, fs_file):
    cast_fs = lv.fs_file_t.cast(fs_file)

    try:
        cast_fs.file_d.cast()['file'].close()
    except Exception as e:
        print("fs_close_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_read_cb(drv, fs_file, buf, btr, br):
    cast_fs = lv.fs_file_t.cast(fs_file)

    try:
        tmp_data = cast_fs.file_d.cast()['file'].read(btr)
        # tmp_len = len(tmp_data)
        buf.__dereference__(btr)[0:len(tmp_data)] = tmp_data
        br.__dereference__(4)[0:4] = struct.pack("<L", len(tmp_data))

    except Exception as e:
        print("fs_read_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_seek_cb(drv, fs_file, pos):
    cast_fs = lv.fs_file_t.cast(fs_file)

    try:
        # to =
        cast_fs.file_d.cast()['file'].seek(pos, 0)
    except Exception as e:
        print("fs_seek_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_tell_cb(drv, fs_file, pos):
    cast_fs = lv.fs_file_t.cast(fs_file)

    try:
        tpos = cast_fs.file_d.cast()['file'].tell()
        pos.__dereference__(4)[0:4] = struct.pack("<L", tpos)
    except Exception as e:
        print("fs_tell_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_write_cb(drv, fs_file, buf, btw, bw):
    cast_fs = lv.fs_file_t.cast(fs_file)

    try:
        wr = cast_fs.file_d.cast()['file'].write(buf[0:btw])
        bw.__dereference__(4)[0:4] = struct.pack("<L", wr)
    except Exception as e:
        print("fs_write_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_register(fs_drv, letter):

    fs_drv.init()
    fs_drv.letter = ord(letter)
    fs_drv.open_cb = fs_open_cb
    fs_drv.read_cb = fs_read_cb
    fs_drv.write_cb = fs_write_cb
    fs_drv.seek_cb = fs_seek_cb
    fs_drv.tell_cb = fs_tell_cb
    fs_drv.close_cb = fs_close_cb

    fs_drv.register()
