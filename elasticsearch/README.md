# FAANG Elasticsearch Configs

**Initialize Helm**
```bash
helm init
```
**Install Tiller**
```bash
kubectl create serviceaccount -n kube-system tiller
kubectl create clusterrolebinding tiller-cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:tiller
helm init --service-account tiller \
  --override spec.selector.matchLabels.'name'='tiller',spec.selector.matchLabels.'app'='helm' \
  --output yaml | sed 's@apiVersion: extensions/v1beta1@apiVersion: apps/v1@' | kubectl apply -f -
```

**Add Elasticsearch repo and install it**
```bash
helm repo add elastic https://helm.elastic.co
helm install --name elasticsearch elastic/elasticsearch \
  --set service.type=LoadBalancer
```

**Install ingress**
```bash
kubectl create -f ingress.yml
```
