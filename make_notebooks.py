from textwrap import dedent
import nbformat as nbf
from inspect import getsource
import re

import mimikit as mmk


def colab_setup():
    title = nbf.v4.new_markdown_cell("""\
## Connect to your GDrive 
In order to train the network on your data, create a directory named `data/`
in the current working directory (cwd) of this notebook (when on colab and connected to gdrive
this would be the `MyDrive/` directory in your gdrive account) and put audio files in it. \
""")
    mount_drive = nbf.v4.new_code_cell("""\
from google.colab import drive
drive.mount('/gdrive')
# this set the cwd of the notebook
%cd /gdrive/MyDrive \
""")
    install = nbf.v4.new_markdown_cell("""\
### Install `mimikit`\
""")
    pip = nbf.v4.new_code_cell(f"""\
%pip uninstall torchtext -y
%pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
%pip install mimikit[colab]=={mmk.__version__}\
""")
    imports = nbf.v4.new_code_cell(f"""\
# colab crashes if following import is done within mimikit
import pytorch_lightning as pl\
""")
    return [title, mount_drive, install, pip, imports]


def demo_to_notebook(demo, out_file, colab=False):
    code = getsource(demo)
    code = code.strip("def demo():\n")
    is_separator = re.compile(r"(\"\"\"[^\n]*\"\"\"[\n]*)")
    parts = re.split(is_separator, code)
    nb = nbf.v4.new_notebook()
    cells = []
    if colab:
        nb["metadata"].update(dict(accelerator='GPU'))
        cells += colab_setup()
    else:
        warning = nbf.v4.new_markdown_cell(f"""\
this notebook assumes you already installed mimikit on your system through the command-line
```bash
pip install mimikit[torch]=={mmk.__version__}
```
""")
        cells += [warning]
    for part in parts:
        if not part:
            continue
        part = dedent(part).strip()
        if part.startswith('"""'):
            cells += [nbf.v4.new_markdown_cell(part.strip('"""'))]
        else:
            part = part.strip('\n\n').strip("\n")
            if part:
                cells += [nbf.v4.new_code_cell(part)]
    signature = nbf.v4.new_markdown_cell("""<img src="https://ktonal.com/k-circle-bw.png" alt="logo" width="75"/>""")
    nb['cells'] = cells + [signature]
    with open(out_file, 'w') as f:
        nbf.write(nb, f)


if __name__ == '__main__':
    import os
    import mimikit.demos as demos

    roots = [
        './demos/plain',
        './demos/colab',
    ]

    demos = {
        "freqnet.ipynb": demos.freqnet.demo,
        "sample-rnn.ipynb": demos.srnn.demo,
        "seq2seq.ipynb": demos.seq2seq.demo,
        "ensemble-generator.ipynb": demos.ensemble_generator.demo,
        "generate.ipynb": demos.generate_from_checkpoint.demo,
        "clusterizer.ipynb": demos.clusterizer_app.demo
    }

    for root in roots:
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)
        for name, demo in demos.items():
            if "colab" in root and "clusterizer" in name:
                continue
            demo_to_notebook(demo, os.path.join(root, name), colab='colab' in root)

