import glob
import os
import shutil
import importlib
from urllib.parse import urlparse

from basicsr.utils.download_util import load_file_from_url
from modules import shared
from modules.upscaler import Upscaler
from modules.paths import script_path, models_path


def load_models(model_path: str, model_url: str = None, command_path: str = None, ext_filter=None, download_name=None) -> list:
    """
    A one-and done loader to try finding the desired models in specified directories.

    @param download_name: Specify to download from model_url immediately.
    @param model_url: If no other models are found, this will be downloaded on upscale.
    @param model_path: The location to store/find models in.
    @param command_path: A command-line argument to search for models in first.
    @param ext_filter: An optional list of filename extensions to filter by
    @return: A list of paths containing the desired model(s)
    """
    # If the ext_filter is not specified, we'll use an empty list
    output = []

        # We'll start with an empty list of places to look for models
    if ext_filter is None:
            # If the command_path is specified, we'll look for a pretrained_models folder in the command_path
        ext_filter = []

    try:
        places = []
            # If the pretrained_models folder doesn't exist, we'll just use the command_path

        if command_path is not None and command_path != model_path:
        # We'll always look in the model_path
            pretrained_path = os.path.join(command_path, 'experiments/pretrained_models')
            if os.path.exists(pretrained_path):
        # We'll look through all the places we've specified
                print(f"Appending path: {pretrained_path}")
            # If the place exists, we'll look through all the files in it
                places.append(pretrained_path)
            elif os.path.exists(command_path):
                places.append(command_path)

        places.append(model_path)

        for place in places:
            if os.path.exists(place):
                    # If the file is a directory, we'll skip it
                for file in glob.iglob(place + '**/**', recursive=True):
                    full_path = file
                    # If the file doesn't have the right extension, we'll skip it
                    if os.path.isdir(full_path):
                        continue
                    if len(ext_filter) != 0:
                        model_name, extension = os.path.splitext(file)
                    # If the file is already in the output list, we'll skip it
                        if extension not in ext_filter:
                            continue
        # If we didn't find any models and the model_url is specified, we'll download it
                    if file not in output:
                        output.append(full_path)

        if model_url is not None and len(output) == 0:
            if download_name is not None:
                dl = load_file_from_url(model_url, model_path, True, download_name)
                output.append(dl)
            else:
                output.append(model_url)

    except Exception:
        pass

    return output


def friendly_name(file: str):
    if "http" in file:
        file = urlparse(file).path

    file = os.path.basename(file)
    model_name, extension = os.path.splitext(file)
    return model_name


def cleanup_models():
    # This code could probably be more efficient if we used a tuple list or something to store the src/destinations
    # and then enumerate that, but this works for now. In the future, it'd be nice to just have every "model" scaler
    # somehow auto-register and just do these things...
    root_path = script_path
    src_path = models_path
    dest_path = os.path.join(models_path, "Stable-diffusion")
    move_files(src_path, dest_path, ".ckpt")
    src_path = os.path.join(root_path, "ESRGAN")
    dest_path = os.path.join(models_path, "ESRGAN")
    move_files(src_path, dest_path)
    src_path = os.path.join(root_path, "gfpgan")
    dest_path = os.path.join(models_path, "GFPGAN")
    move_files(src_path, dest_path)
    src_path = os.path.join(root_path, "SwinIR")
    dest_path = os.path.join(models_path, "SwinIR")
    move_files(src_path, dest_path)
    src_path = os.path.join(root_path, "repositories/latent-diffusion/experiments/pretrained_models/")
    dest_path = os.path.join(models_path, "LDSR")
    move_files(src_path, dest_path)


def move_files(src_path: str, dest_path: str, ext_filter: str = None):
    try:
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        if os.path.exists(src_path):
            for file in os.listdir(src_path):
                fullpath = os.path.join(src_path, file)
                if os.path.isfile(fullpath):
                    if ext_filter is not None:
                        if ext_filter not in file:
                            continue
                    print(f"Moving {file} from {src_path} to {dest_path}.")
                    try:
                        shutil.move(fullpath, dest_path)
                    except:
                        pass
            if len(os.listdir(src_path)) == 0:
                print(f"Removing empty folder: {src_path}")
                shutil.rmtree(src_path, True)
    except:
        pass


def load_upscalers():
    sd = shared.script_path
    # We can only do this 'magic' method to dynamically load upscalers if they are referenced,
    # so we'll try to import any _model.py files before looking in __subclasses__
    modules_dir = os.path.join(sd, "modules")
    for file in os.listdir(modules_dir):
        if "_model.py" in file:
            model_name = file.replace("_model.py", "")
            full_model = f"modules.{model_name}_model"
            try:
                importlib.import_module(full_model)
            except:
                pass
    datas = []
    c_o = vars(shared.cmd_opts)
    for cls in Upscaler.__subclasses__():
        name = cls.__name__
        module_name = cls.__module__
        module = importlib.import_module(module_name)
        class_ = getattr(module, name)
        cmd_name = f"{name.lower().replace('upscaler', '')}_models_path"
        opt_string = None
        try:
            if cmd_name in c_o:
                opt_string = c_o[cmd_name]
        except:
            pass
        scaler = class_(opt_string)
        for child in scaler.scalers:
            datas.append(child)

    shared.sd_upscalers = datas
