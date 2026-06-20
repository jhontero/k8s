# Microservicio K8S - Universidad de La Sabana

Microservicio desplegado en Kubernetes mediante Helm, con despliegue continuo automatizado usando ArgoCD (GitOps) y un pipeline de CI/CD en GitHub Actions.

## Tecnologías usadas

- **Docker** — contenerización del microservicio
- **Kubernetes** — orquestación de contenedores
- **Helm** — gestión de configuraciones y despliegue (charts)
- **ArgoCD** — despliegue continuo (CD) mediante GitOps
- **GitHub Actions** — integración continua (CI): build, push de imagen y actualización del chart

## Estructura del proyecto

```
.
├── app/
│   ├── app.py              # Microservicio Flask
│   ├── requirements.txt
│   └── Dockerfile
├── helm/
│   └── k8s/
│       ├── Chart.yaml
│       ├── values.yaml     # Configuración del despliegue
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           └── _helpers.tpl
├── argocd/
│   └── application.yaml    # Definición de la app en ArgoCD
└── .github/
    └── workflows/
        └── ci-cd.yaml       # Pipeline de CI/CD
```

## Requisitos previos

| Herramienta | Verificar instalación | Instalar (Windows) |
|---|---|---|
| Docker Desktop (incluye Kubernetes) | `docker --version` y `kubectl get nodes` | https://www.docker.com/products/docker-desktop/ → Settings → Kubernetes → Enable Kubernetes |
| kubectl | `kubectl version --client` | `winget install -e --id Kubernetes.kubectl` |
| Helm | `helm version` | `winget install Helm.Helm` |
| Git | `git --version` | `winget install --id Git.Git -e --source winget` |

Confirma que el contexto de `kubectl` apunte al clúster local de Docker Desktop:

```powershell
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl get nodes
```

## 1. Clonar el repositorio

```powershell
git clone https://github.com/jhontero/k8s.git
cd k8s
```

## 2. Desplegar ArgoCD en el clúster

ArgoCD corre dentro del propio clúster de Kubernetes, no en tu máquina:

```powershell
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verifica que todos los pods queden en estado `Running` (puede tardar uno o dos minutos):

```powershell
kubectl get pods -n argocd
```

### Acceder a la interfaz de ArgoCD

```powershell
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Abre en el navegador: `https://localhost:8080`

Usuario: `admin`. Para obtener la contraseña inicial:

```powershell
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | Out-String | %{[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_.Trim()))}
```

## 3. Crear la aplicación en ArgoCD

El archivo `argocd/application.yaml` ya define el microservicio, apuntando a este repositorio y al chart de Helm en `helm/k8s`:

```powershell
kubectl apply -f argocd/application.yaml
```

Verifica que se creó correctamente:

```powershell
kubectl get application -n argocd
```

Como la aplicación tiene `syncPolicy.automated` con `selfHeal: true`, ArgoCD sincroniza el clúster automáticamente con lo que esté en la rama `main` del repositorio — no es necesario aplicar el chart de Helm manualmente.

## 4. Verificar el despliegue

```powershell
kubectl get pods
kubectl get svc k8s
kubectl get application k8s -n argocd
```

El pod debe estar en estado `Running` (`READY 1/1`), y la aplicación en ArgoCD debe mostrar `SYNC STATUS: Synced` y `HEALTH STATUS: Healthy`.

## 5. Acceder al microservicio

El `Service` está configurado como `NodePort` en `helm/k8s/values.yaml`. Para saber en qué puerto quedó expuesto en tu máquina (Kubernetes puede asignarlo automáticamente si el solicitado no está disponible):

```powershell
kubectl get svc k8s
```

La columna `PORT(S)` mostrará algo como `5000:3XXXX/TCP` — el número después de los dos puntos es el puerto accesible desde tu navegador:

```
http://localhost:3XXXX/
```

### Alternativa con port-forward (siempre funciona, sin depender del NodePort)

```powershell
kubectl port-forward svc/k8s 5000:5000
```

Y accede a `http://localhost:5000/`.

## 6. Flujo de CI/CD automático

Cada vez que se hace `git push` a la rama `main`:

1. **GitHub Actions** construye la imagen Docker del microservicio y la publica en Docker Hub, con dos tags: `latest` y el SHA del commit.
2. **GitHub Actions** actualiza automáticamente el campo `tag` en `helm/k8s/values.yaml` con el SHA de la nueva imagen, y hace commit y push de ese cambio.
3. **ArgoCD**, que vigila este repositorio, detecta el cambio en `values.yaml` y sincroniza el clúster automáticamente, desplegando la nueva versión de la imagen (rolling update).

No es necesario ejecutar ningún comando manual para que el despliegue ocurra — todo el ciclo es automático una vez configurado.

### Forzar sincronización manual (opcional)

Si no quieres esperar el ciclo de revisión periódico de ArgoCD:

```powershell
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

En la interfaz web (`https://localhost:8080`), busca la aplicación `k8s` y haz clic en **Refresh** y luego **Sync**.

## Comandos útiles de diagnóstico

```powershell
kubectl get pods                          # Estado de los pods
kubectl logs <nombre-del-pod>             # Logs del microservicio
kubectl describe application k8s -n argocd # Detalle y eventos de ArgoCD
kubectl rollout restart deployment k8s    # Forzar reinicio del despliegue
helm template helm/k8s                    # Ver el manifiesto generado por el chart
```
