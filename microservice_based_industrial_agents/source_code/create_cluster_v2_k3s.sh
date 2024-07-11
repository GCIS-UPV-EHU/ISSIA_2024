#echo "########## ADDING YOUR USER TO SUDOERS FILE ##########"
#echo "If you already have added your current user to sudoers file,"
#echo "you can skip this part and press any key to continue"
#echo
#echo "Otherwise, execute:"
#echo "  echo \"username  ALL=(ALL) NOPASSWD:ALL\" | sudo tee /etc/sudoers.d/username"
#echo "where 'username' is your current user"
#read -p "And press Ctrl+C to execute the script again"
#echo

#echo "########## INSTALLING MULTIPASS ##########"
#sudo snap install multipass
#echo

#echo "########## GENERATING KEYS ##########"
#echo "If you already have ~/.ssh/id_rsa and ~/.ssh/id_rsa.pub, you can skip this part"
#echo
#echo "Otherwise, execute 'ssh-keygen' to create a private/public key"
#echo
#read -p "Press any key to continue "
#echo
#pub_key=$(cat ~/.ssh/id_rsa.pub)
#echo "ssh_authorized_keys:" > multipass.yaml
#echo "  - "$pub_key >> multipass.yaml

#echo "########## CREATING SHARED FOLDER AMONG HOST AND NODES ##########"
#mkdir shared
#echo

echo "########## INSTALLING K3S MASTER ON HOST ##########"
host_ip=$(ifconfig ens33 | grep "inet " | awk -F: '{print $1}' | awk '{print $2}')
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -s - --node-ip $host_ip
echo

echo "########## CREATING NODES ##########"
read -p "Enter number of nodes: " number
for i in $(seq 1 $number)
do
  node_name="node"$i
  echo "########## CREATING "$node_name" ##########"
  multipass launch 20.04 --name $node_name --cpus 1 --memory 2G --disk 5G --cloud-init multipass.yaml 
  echo
  
  #echo "########## MOUNTING SHARED FOLDER ON "$node_name" MULTIPASS INSTANCE ##########"
  #multipass mount shared $node_name
  #echo
  
  echo "########## INSTALLING K3S AGENT ON "$node_name" ##########"
  node_ip="$(multipass list | tail -n -1 | awk '{ print $3 }')"
  k3s_token=$(sudo cat /var/lib/rancher/k3s/server/node-token)
  remote_cmd="'curl -sfL https://get.k3s.io | K3S_URL=https://"$host_ip":6443 K3S_TOKEN="$k3s_token" sh -s - --node-label node-type=multipass'"
  echo $remote_cmd
  

  ssh -o StrictHostKeyChecking=no ubuntu@$node_ip \'$remote_cmd\'
  echo
  
  free -m && sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches' && free -m
  echo
done

sudo k3s kubectl label nodes cluster node-type=master

# Installing cluster features
sleep 10 # wait until the cluster is ready
echo "-------- INSTALLING KUBERNETES EXTENSION --------"
sudo k3s kubectl apply -f /home/issia/KubernetesExtension/authorizations
sleep 1
sudo k3s kubectl apply -f /home/issia/KubernetesExtension/application-controller-deployment.yaml
sudo k3s kubectl apply -f /home/issia/KubernetesExtension/microservice-controller-deployment.yaml

echo "-------- INSTALLING NODE-RED IN K3S CLUSTER --------"
sudo k3s kubectl apply -f /home/issia/NodeRED/data-persistent-volume-nodered.yaml
sleep 1
sudo k3s kubectl apply -f /home/issia/NodeRED/
echo "-------- INSTALLING KUBERNETES DASHBOARD IN K3S CLUSTER --------"
/home/issia/Kubernetes_dashboard/setup.sh
cp -f /home/issia/Kubernetes_dashboard/dashboard_token.txt /home/issia/Desktop




