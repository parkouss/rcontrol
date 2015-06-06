
def copy_file(src_os, src, dest_os, dest, chunk_size=16384):
    with src_os.open(src, 'rb') as fr:
        with dest_os.open(dest, 'wb') as fw:
            data = fr.read(chunk_size)
            while data:
                fw.write(data)
                data = fr.read(chunk_size)
