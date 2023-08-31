#!/bin/bash -eux

# activate venv
source ~/venv/bin/activate
# install python dependency 
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r ./requirements.txt

# cp font file for matplotlib chinese
#mpldatadir=$(python -c "import matplotlib; print(matplotlib.get_data_path())")
#cp ./fonts/simhei.ttf ${mpldatadir}/fonts/ttf/


# Install starship prompt (optional)
curl -fsSL https://starship.rs/install.sh -o starship_install.sh
echo "dev123" | sudo --stdin sh starship_install.sh -y
rm starship_install.sh
mkdir -p ~/.config/fish && echo "starship init fish | source" >> ~/.config/fish/config.fish
fish -c "set -U fish_greeting"