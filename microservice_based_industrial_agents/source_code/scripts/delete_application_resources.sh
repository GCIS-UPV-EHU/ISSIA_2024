###### AUTHOR: Ekaitz Hurtado ######

echo "PROGRAM TO REMOVE ALL RESOURCES RELATED TO A DEPLOYED APPLICATION"
read -p "First, enter the application name: " app_name

sudo k3s kubectl delete deploy numbergeneratorbutton-$app_name
sudo k3s kubectl delete deploy numberprocessor-$app_name
sudo k3s kubectl delete deploy numberdisplay-$app_name

sudo k3s kubectl delete svc numberprocessor-$app_name
sudo k3s kubectl delete svc numberdisplay-$app_name

sudo k3s kubectl delete app $app_name
sudo k3s kubectl delete microsvc numbergeneratorbutton-$app_name
sudo k3s kubectl delete microsvc numberprocessor-$app_name
sudo k3s kubectl delete microsvc numberdisplay-$app_name

for i in $(seq 1 10)
do
  if kubectl get deploy numberprocessor-$i-$app_name | grep -q "numberprocessor-"$i
  then
  sudo k3s kubectl delete deploy numberprocessor-$i-$app_name
  sudo k3s kubectl delete svc numberprocessor-$i-$app_name
  sudo k3s kubectl delete microsvc numberprocessor-$i-$app_name
  fi
done

read -p "Does the application have a custom component? (y/n) " custom_comp_boolean

if [[ $custom_comp_boolean == "y" ]]
then
read -p "Enter the custom component name: " custom_comp_name
sudo k3s kubectl delete deploy $custom_comp_name-$app_name
sudo k3s kubectl delete svc $custom_comp_name-$app_name
sudo k3s kubectl delete microsvc $custom_comp_name-$app_name

fi

echo "All resources removed!"
