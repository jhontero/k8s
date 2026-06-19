# Trabajo K8S - Universidad de La Sabana

## Tecnologías usadas
- Docker (contenedor del microservicio)
- Kubernetes (orquestación)
- Helm (gestión de configuraciones)
- ArgoCD (GitOps / despliegue continuo)
- GitHub Actions (CI pipeline)

## Cómo ejecutar localmente
1. `docker build -t mi-microservicio:v1 ./app`
2. `docker run -p 5000:5000 mi-microservicio:v1`

## Flujo de despliegue
Un `git push` a `main` dispara el pipeline que construye y publica la imagen.
ArgoCD detecta el cambio en el Helm chart y sincroniza el clúster automáticamente.

## Comandos útiles
```bash
kubectl get pods
kubectl get svc
helm list
argocd app get mi-microservicio
```