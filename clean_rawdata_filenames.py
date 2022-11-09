import argparse
import os

# cli-params
ap = argparse.ArgumentParser(description="pamudoan - filename cleanup for raw data.")
ap.add_argument("-d", "--dir", required=True, default='',
    help="Path to the raw data (PDFs).")
ap.add_argument("-p", "--prefix", required=False, default='',
    help="Optional prefix for the every new filename. Default=''.")
ap.add_argument("-s", "--simulate", required=False, action='store_true', default=False,
    help="Do not rename filenames. Only simulate. Default=False.")
args = vars(ap.parse_args())


rawdata_path  = os.path.abspath(args['dir']) #'/home/pib/windows_hdd/Nextcloud/BRISE-WP5-Daten/Daten/analoge_baueinreichungen'
rawdata_files = os.listdir(rawdata_path)
prefix        = args['prefix']


for fn in rawdata_files:
    fn_new = prefix + fn.lower()
    fn_new = fn_new.replace('. ', '_')
    fn_new = fn_new.replace(', ', '_')
    fn_new = fn_new.replace('(', '_')
    fn_new = fn_new.replace(')', '_')
    fn_new = fn_new.replace('|', '_')
    fn_new = fn_new.replace('/', '_')
    fn_new = fn_new.replace('\\', '_')
    fn_new = fn_new.replace(',', '_')
    fn_new = fn_new.replace('`', '')
    fn_new = fn_new.replace('´', '')
    fn_new = fn_new.replace(' ', '_')
    fn_new = fn_new.replace('ä', 'ae')
    fn_new = fn_new.replace('ö', 'oe')
    fn_new = fn_new.replace('ü', 'ue')
    fn_new = fn_new.replace('ß', 'sz')
    fn_new = fn_new.replace('.pdf.pdf', '.pdf')
    
    src_fn = '{}/{}'.format(rawdata_path, fn)
    dst_fn = '{}/{}'.format(rawdata_path, fn_new)
    print("rename '{}'\n {} => {}".format(fn, src_fn, dst_fn))
    try:
        if not args['simulate']:
            os.rename(src_fn, dst_fn)
            print("ok")
    except Exception as e:
        print("ERROR! ", e)
print('done.')