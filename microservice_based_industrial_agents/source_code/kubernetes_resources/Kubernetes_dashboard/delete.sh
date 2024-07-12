sudo k3s kubectl delete ns kubernetes-dashboard
sudo k3s kubectl delete clusterrolebinding kubernetes-dashboard
sudo k3s kubectl delete clusterrole kubernetes-dashboard

sudo k3s kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml
sudo k3s kubectl delete -f /home/issia/Kubernetes_dashboard/dashboard.admin-user.yml -f /home/issia/Kubernetes_dashboard/dashboard.admin-user-role.yml
