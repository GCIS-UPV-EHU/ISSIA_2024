###### AUTHOR: Oskar Casquero ######

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
#sudo kubectl config set-context default
kubectl delete deploy --all
kubectl delete node --all
sudo /usr/local/bin/k3s-uninstall.sh
sudo rm -rf /var/lib/rancher/k3s

read -p "Enter number of nodes: " number
for i in $(seq 1 $number)
do
  if [ $i -le 9 ]
  then    echo "Deleting node$i..."
    multipass delete node$i
  else
    echo "Deleting node$i..."
    multipass delete node$i
  fi
done
multipass purge

