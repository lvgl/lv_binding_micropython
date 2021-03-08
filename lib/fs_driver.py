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

    try:
        f = open(path, p_mode)
        ptr = lv.C_Pointer.cast(fs_file)
        ptr.ptr_val = {'file' : f}
    except Exception as e:
        print("fs_open_callback() exception: ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_close_cb(drv, fs_file):
    try:
        fs_file.cast()['file'].close()
    except Exception as e:
        print("fs_close_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_read_cb(drv, fs_file, buf, btr, br):
    try:
        tmp_data = fs_file.cast()['file'].read(btr)
        # tmp_len = len(tmp_data)
        buf.__dereference__(btr)[0:len(tmp_data)] = tmp_data
        br.__dereference__(4)[0:4] = struct.pack("<L", len(tmp_data))

    except Exception as e:
        print("fs_read_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_seek_cb(drv, fs_file, pos):
    try:
        # to =
        fs_file.cast()['file'].seek(pos, 0)
    except Exception as e:
        print("fs_seek_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_tell_cb(drv, fs_file, pos):
    try:
        tpos = fs_file.cast()['file'].tell()
        pos.__dereference__(4)[0:4] = struct.pack("<L", tpos)
    except Exception as e:
        print("fs_tell_callback() exception ", uerrno.errorcode[e.args[0]])
        return lv.FS_RES.FS_ERR

    return lv.FS_RES.OK


def fs_write_cb(drv, fs_file, buf, btw, bw):
    try:
        wr = fs_file.cast()['file'].write(buf[0:btw])
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
