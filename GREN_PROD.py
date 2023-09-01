import os
import datetime
import socket
import subprocess

# Variables de configuración
CONFIG = {
    'carp_inicial': r"C:\Estadistica",
    'carp_out_cfg': r"C:\Grenouille\OUT\cfg",
    'carp_out_dat': r"C:\Grenouille\OUT\dat",
    'carp_out_esc': r"C:\Grenouille\OUT\esc",
    'carp_out_log': r"C:\Grenouille\OUT\log",
    'carp_out_zip': r"C:\Grenouille\OUT\zip",
    'carp_ya_cfg': r"C:\Grenouille\YA\cfg",
    'carp_ya_dat': r"C:\Grenouille\YA\dat",
    'carp_ya_esc': r"C:\Grenouille\YA\esc",
    'carp_ya_log': r"C:\Grenouille\YA\log",
    'carp_ya_zip': r"C:\Grenouille\YA\zip",
    'carp_error_dat': r"C:\Grenouille\ERROR\dat",
    'carp_wscp': r"C:\Grenouille\SW\Portables\WinSCP\WinSCP.com",
    'carp_7z': r"c:\Program Files\7-Zip\7z.exe",
    'clave_7z': "1PhtzBZ1P1P_",
    'server_ip': "dl220.dinaserver.com",
    'server_port': 22,
    'server_hostkey': "HhPYtIAcRoH2ScmIxvvlyeNJ0TqmiwZpOZJINLT8RWU=",
    'server_username': "grenouille",
    'server_password': "Gr3N0u1ll3@22",
    'server_path': r"/home/GRE/ENTRADA_FICHEROS/FICHEROS/"
}

log_path = os.path.join(CONFIG['carp_out_log'], f"{socket.gethostname()}-actions.log")

def log_action(message):
    """Log actions and print messages."""
    now = datetime.datetime.now()
    with open(log_path, 'a') as f:
        f.write(f"[{now}] - {message}\n")
    print(f"[{now}] - {message}")

def ensure_directory_exists(directory):
    """Ensure directory exists, if not, create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_zip_filename(folder_name):
    """Generate the correct name for the .7z file."""
    hostname = socket.gethostname()
    current_time = datetime.datetime.now().strftime('%H%M%S')
    return f"{hostname}-{folder_name}-{current_time}.7z"

def move_directory(src_path, dst_path):
    """Move directories, handle if file already exists."""
    if os.path.exists(dst_path):
        dst_path += f"_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.rename(src_path, dst_path)

def compress_directory(src_directory):
    """Compress directory using 7z."""
    output_file = os.path.join(CONFIG['carp_out_zip'], generate_zip_filename(src_directory))
    cmd = [
        CONFIG['carp_7z'], "a", "-t7z", output_file, f"{src_directory}/*",
        f"-p{CONFIG['clave_7z']}", "-mhe=on", "-sdel"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_action(f"Archivos comprimidos y guardados en {output_file} desde {src_directory}\n{result.stdout}")
    return output_file

def winscp_upload_file(file_path):
    """Upload file using WinSCP."""
    script_content = f'''
    open sftp://{CONFIG['server_username']}:{CONFIG['server_password']}@{CONFIG['server_ip']}:{CONFIG['server_port']} -hostkey="{CONFIG['server_hostkey']}"
    put {file_path} {CONFIG['server_path']}
    exit
    '''
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(script_content.encode())
    cmd = [CONFIG['carp_wscp'], "/script=" + tmp_file.name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_action(f"Archivo {file_path} subido\n{result.stdout}")
    os.remove(tmp_file.name)

if __name__ == '__main__':
    directories_to_check = [
        CONFIG[key] for key in CONFIG if key.startswith('carp_')
    ]
    for directory in directories_to_check:
        ensure_directory_exists(directory)

    for folder in os.listdir(CONFIG['carp_inicial']):
        folder_path = os.path.join(CONFIG['carp_inicial'], folder)
        if os.path.isdir(folder_path):
            compressed_file = compress_directory(folder_path)
            winscp_upload_file(compressed_file)
            move_directory(folder_path, os.path.join(CONFIG['carp_ya_dat'], folder))
