#!/bin/bash

# Install git and python3
sudo apt-get update
sudo apt-get install -y git python3-venv python3-pip git sshpass

# Setup SSH keys (echo hardcoded with cat EOF)
cat << 'EOF' > /home/vagrant/.ssh/id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEA1Q4vswodf/4E6Hgp/MRBagiW3pYaPX22FETNyC5rIU4PcDGv2WZ/
Ub6PA5t8yZyXmGpaCuPqIQamyU2IQNV4p5o1aKYaThK2bSA9aAEYhRWfOnaP9SuZ3m7IQ8
diJBeTKrZ35Y7S5+Mh+sV0HqtPq2QQE80TwevkkNAckZvOigP7zCaF8EpIrewSnSmfX9Xc
Kf73dJevkHasTxfsmvcZ4uz0ACae+frsWHPQwZURm4Ho8USH/xMENcy78zWqtggvlzJe0O
vapYX7J1CYZG0f/Uem5FPLzuiV4UcfkbeybqpBVhRrfxxdltZ0xsmhYGIgBvvQzvYYa0/x
O5kzD8+j4QAAA8gmv41bJr+NWwAAAAdzc2gtcnNhAAABAQDVDi+zCh1//gToeCn8xEFqCJ
belho9fbYURM3ILmshTg9wMa/ZZn9Rvo8Dm3zJnJeYaloK4+ohBqbJTYhA1XinmjVophpO
ErZtID1oARiFFZ86do/1K5nebshDx2IkF5MqtnfljtLn4yH6xXQeq0+rZBATzRPB6+SQ0B
yRm86KA/vMJoXwSkit7BKdKZ9f1dwp/vd0l6+QdqxPF+ya9xni7PQAJp75+uxYc9DBlRGb
gejxRIf/EwQ1zLvzNaq2CC+XMl7Q69qlhfsnUJhkbR/9R6bkU8vO6JXhRx+Rt7JuqkFWFG
t/HF2W1nTGyaFgYiAG+9DO9hhrT/E7mTMPz6PhAAAAAwEAAQAAAQBGllGlXteRPUbBAnbe
wOLvT3M0wcRl1Q2LP5RyGzbxLNyejke1nmjWW20kg9JfNZtgKvQ0IXjDgmGl1iMrX85+sO
+7ATU74qVAGGtf1uUZyqUbiIZ/cveio0+EbT2NuaXPg+7LRnuHyk/KtrqXIqjdnuRYuxwt
poruk5SzhUxzmu127Q1TnPI/lqZml1O/j+lKdxYW9y0kLAb0zWtzz/V5CMAGRuMRe67VUE
B+uV5F7Yhi3udSczbFWePc7/v8Noehck4bbJSR6iezN106rRGILjo6hswp3eSFiOP0X5yC
KGt6h2UxzRuumRshlHJqs2sX7hAZqn3/mb4z9+7nuTZVAAAAgQDZ86cBEhDZsiyExCbncn
GXB5YNwtpgsIw/Y/fpwTkA5Q74ZceULQ6aVV1/XoSjmI3s9dTQl0gKexGiuUpFq2d/8Ovk
acQ0s2+k/m2B9V6M+9O4mLA4EJ9tIAEUSOYKhg6NqueSOoobWVnjJhFV6Y//I7ed35TObF
bqOykkueY8ywAAAIEA76ZSxiv/rxjcwMIx//7/scognee6tepJqwxNAl412feRxrR0S5O0
YIcziuDLA411x/jT59r6ngbOZ+GEoOEjVUZBro0kZlTcO3l/w2RN5hERvXU6cE+Mq22+Ai
7TPtw/AfKqI6MMNGXyVHFBqkU0yUoDFWmJ9zb0jIC90ksdQvMAAACBAOOXX0hlLUeHNSSK
+WMYr0uJKkKbIEu6auPYsD4cIGqlo2QbngfkEV5m1PwSZ2gUxSLvRotNuFeOnaJ5zPJX4G
7uezFk16p5KmJR7CIAacjsOagDYjxyNlwLaWe+aa6Jjbbt8397u94FMwF4nKIrA2RN9x3M
1rqF14jVtp4j5qrbAAAAEmxsbWRlZmVuc2VAbWFzdGVycw==
-----END OPENSSH PRIVATE KEY-----
EOF

cat << 'EOF' > /home/vagrant/.ssh/id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDVDi+zCh1//gToeCn8xEFqCJbelho9fbYURM3ILmshTg9wMa/ZZn9Rvo8Dm3zJnJeYaloK4+ohBqbJTYhA1XinmjVophpOErZtID1oARiFFZ86do/1K5nebshDx2IkF5MqtnfljtLn4yH6xXQeq0+rZBATzRPB6+SQ0ByRm86KA/vMJoXwSkit7BKdKZ9f1dwp/vd0l6+QdqxPF+ya9xni7PQAJp75+uxYc9DBlRGbgejxRIf/EwQ1zLvzNaq2CC+XMl7Q69qlhfsnUJhkbR/9R6bkU8vO6JXhRx+Rt7JuqkFWFGt/HF2W1nTGyaFgYiAG+9DO9hhrT/E7mTMPz6Ph llmdefense@masters
EOF

chmod 600 /home/vagrant/.ssh/id_rsa
chmod 644 /home/vagrant/.ssh/id_rsa.pub
chown vagrant:vagrant /home/vagrant/.ssh/id_rsa
chown vagrant:vagrant /home/vagrant/.ssh/id_rsa.pub

# Add github.com to known_hosts to avoid SSH prompt
ssh-keyscan github.com >> /home/vagrant/.ssh/known_hosts
chmod 644 /home/vagrant/.ssh/known_hosts
chown vagrant:vagrant /home/vagrant/.ssh/known_hosts

# git clone goad
GOAD_REPO=/home/vagrant/GOAD
GIT_FOLDER=$GOAD_REPO/.git
if [ ! -d $GIT_FOLDER ]
then
    rm -rf $GOAD_REPO
    git clone https://github.com/DeadPackets/GOAD.git $GOAD_REPO
    cd $GOAD_REPO
    git checkout llm-ad-defense
    git submodule init
    git submodule update --init --recursive
    # git checkout -b v3-beta origin/v3-beta
else
    cd $GOAD_REPO
    git pull
fi

# Install ansible and pywinrm
python3 -m pip install --upgrade pip
cd $GOAD_REPO
python3 -m pip install -r requirements.yml

cd $GOAD_REPO/ansible
/home/vagrant/.local/bin/ansible-galaxy install -r requirements.yml

# set color
sudo sed -i '/force_color_prompt=yes/s/^#//g' /home/*/.bashrc
sudo sed -i '/force_color_prompt=yes/s/^#//g' /root/.bashrc