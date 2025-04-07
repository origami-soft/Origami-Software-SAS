#!/bin/bash
cd /home/bo/extra-addons/odoo_l10n_ar
git config --global --add safe.directory /home/bo/extra-addons/odoo_l10n_ar
git config core.filemode false
mkdir /root/.ssh/
touch /root/.ssh/known_hosts
ssh-keygen -R bitbucket.org && curl https://bitbucket.org/site/ssh >>~/.ssh/known_hosts
ssh-agent bash -c 'ssh-add /bitbucket_key/bitbucket_key; git pull'
pip3 install -r /home/bo/extra-addons/odoo_l10n_ar/requirements.txt
pip3 install -r /home/bo/extra-addons/odoo_addons_others/requirements.txt
pip3 install --upgrade pyopenssl==22.0.0 cryptography==37.0.4
pip3 install -r /home/bo/extra-addons/odoo_addons_extra/requirements.txt
echo "env['ir.module.module'].upgrade_changed_checksum()" | /home/bo/odoo/odoo-bin shell -d TEST --no-http
python3 /home/bo/odoo/odoo-bin
