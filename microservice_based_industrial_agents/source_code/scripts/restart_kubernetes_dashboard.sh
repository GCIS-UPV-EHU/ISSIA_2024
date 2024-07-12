###### AUTHOR: Ekaitz Hurtado ######

echo "-------- UNINSTALLING KUBERNETES DASHBOARD IN K3S CLUSTER --------"
/home/issia/Kubernetes_dashboard/delete.sh
sleep 1

echo "-------- INSTALLING KUBERNETES DASHBOARD IN K3S CLUSTER --------"
/home/issia/Kubernetes_dashboard/setup.sh
cp -f /home/issia/Kubernetes_dashboard/dasboard_token.txt /home/issia/Desktop
