import os, pathlib
import subprocess
import logging, sys
import shutil

logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

FRONTEND_DIR = "../summarizer-frontend"
BACKEND_DIR = os.getcwd()

DISTRIBUTION_DIR_NAME = "dist"

frontend_path = pathlib.Path(FRONTEND_DIR)
backend_path = pathlib.Path(BACKEND_DIR)

distribution_src_dir = pathlib.Path(os.path.join(frontend_path, DISTRIBUTION_DIR_NAME))
distribution_dest_dir = pathlib.Path(os.path.join(backend_path, DISTRIBUTION_DIR_NAME))

node_modules_dir = pathlib.Path(os.path.join(frontend_path, "node_modules"))

# can pass an optional cmd line arg specifying the environment
# values can be 'development' or 'production'. defaults to 'production'
os.environ["NODE_ENV"] = "production" if (len(sys.argv) < 2) else sys.argv[1]

if not frontend_path.exists():
    logging.critical(f"{frontend_path.resolve()} does not exist.")
    sys.exit(1)

if not frontend_path.is_dir():
    logging.critical(f"{frontend_path.resolve()} is not a directory.")
    sys.exit(1)

if not backend_path.exists():
    logging.critical(f"{backend_path.resolve()} does not exist.")
    sys.exit(1)

if not backend_path.is_dir():
    logging.critical(f"{backend_path.resolve()} is not a directory.")
    sys.exit(1)

# deletes previously created distribution directories to have a clean slate
if distribution_src_dir.exists():
    shutil.rmtree(distribution_src_dir)

if distribution_dest_dir.exists():
    shutil.rmtree(distribution_dest_dir)

# list down the executables which are required to further proceed the build step.
# if any one of the listed executables does not exist, we terminate the build.
required_executable_list = ["node"]

for required_executable in required_executable_list:
    executable_path = shutil.which(required_executable)
    if executable_path is None:
        logging.critical(f"{required_executable} not found.")
        sys.exit(1)

pnpm_path = shutil.which("pnpm")
if pnpm_path is None:
    logging.warning(f"pnpm not found.")

    corepack_path = shutil.which("corepack")
    if corepack_path is None:
        logging.error("corepack not found. cannot install pnpm.")
        sys.exit(1)

    # if corepack is installed, try to install pnpm using corepack
    subprocess.call(["corepack", "enable", "pnpm"], shell=True)

if not node_modules_dir.exists():
    subprocess.call(["pnpm", "install"], shell=True, cwd=frontend_path)


subprocess.call(["pnpm", "run", "build"], shell=True, cwd=frontend_path)
shutil.copytree(distribution_src_dir, distribution_dest_dir)
