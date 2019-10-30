# patroni-class

Master class repo for learning patroni, consul, walg, s3

How to:

# Let's check if we have docker up and running
```bash
docker version
```

# Let's init first 3 containers `h0`, `h1`, `h2`
```bash
ansible-playbook -i inventory init.yml
```

# Let's check if they were deployed ok
```bash
docker ps
```

# Let's check how `dynamic_inventory` is working
```bash
./dynamic_inventory.py
```

# Now use `dynamic_inventory.py` as inventory for consul deploy
```bash
ansible-galaxy install --force -r /workshop/roles/consul/requirements.yml -p /workshop/roles/
ansible-playbook -i dynamic_inventory.py consul.yml
```

# Checking consul cluster is ok
```bash
docker logs h0
```

# Let's perform simple init in postgres cluster
```bash
./dynamic_inventory.py
```
- *(use `less`)*
- `h0` is `172.18.0.2`

# Add one node into cluster with simple init
```bash
ansible-playbook -i dynamic_inventory.py patroni.yml --tags=patroni-init --limit=172.18.0.2
```

# Check if it is up and running
```bash
docker exec -it h0 docker ps
docker exec -it h0 docker logs pg-h0
```

# Let's check dns records for master
```bash
docker exec -it h0 docker exec -it pg-h0 ping master.patroni-class.service.consul
```

# and deploy slave
```bash
ansible-playbook -i dynamic_inventory.py patroni.yml --tags=patroni-init --limit=172.18.0.3
```

## check if it registred
```bash
docker exec -it h0 docker exec -it pg-h0 ping replica.patroni-class.service.consul
```

## and check logs of first slave
```bash
docker exec -it h1 docker logs --tail 100 pg-h1
```

# Let's check if it data replication is working
## Create table on master
```bash
docker exec -it h0 docker exec -it pg-h0 gosu postgres psql -c "CREATE TABLE bins  AS SELECT * FROM GENERATE_SERIES(1, 10000) AS id;"
```

## Read data from slave
```bash
docker exec -it h1 docker exec -it pg-h1 gosu postgres psql -c "SELECT max(id) from bins;"
```

# Let's perform switchover
```bash
docker exec -it h1 docker exec -it pg-h1 bash
patronictl --help
```

# Check existing state
```bash
patronictl -c /var/lib/postgresql/patroni.yml list
```

# Let's do the trick
```bash
patronictl -c /var/lib/postgresql/patroni.yml switchover
```

# Check existing state
```bash
patronictl -c /var/lib/postgresql/patroni.yml list
ping master.patroni-class.service.consul
exit
```

# Let's disconnect current master
```bash
docker network disconnect bridge h1
```

# Failover works
```bash
docker exec -it h0 docker exec -it pg-h0 patronictl -c /var/lib/postgresql/patroni.yml list
```

# Turn on again and see fencing
```bash
docker network connect bridge h1
docker exec -it h0 docker exec -it pg-h0 patronictl -c /var/lib/postgresql/patroni.yml list
```

# Let's init cluster from s3
## we changed scope from `patroni-class` to `patroni-class-walg`
```bash
ansible-playbook -i dynamic_inventory.py patroni.yml --tags=patroni-init-walg --limit=172.18.0.4
```

## and check logs
```bash
docker exec -it h2 docker logs --tail 100 pg-h2
```

# Read data from walg master
```bash
docker exec -it h2 docker exec -it pg-h2 gosu postgres psql -c "SELECT max(id) from walg;"
```

# Telegram group
Join if you have questions: https://t.me/joinchat/BjLKBU-Z1PU5j0-mvhWQCw
