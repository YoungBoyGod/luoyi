## Kubernetes 入门梳理

> 目标：作为初学者，理解常用概念 + 会用 `kubectl` 部署、排错一个典型服务。

### 1. 基础认知
- Kubernetes = “声明式 API + 控制循环”，让集群按你的期望状态自动调节。
- 角色：`Control Plane`（apiserver / scheduler / controller-manager / etcd）负责决策；`Node`（kubelet / kube-proxy / 容器运行时）负责执行。
- 资源对象都存成 YAML（也可以用 JSON），通过 `kubectl apply` 提交。

### 2. 核心对象快速图谱
- `Namespace`：逻辑隔离资源；常见有 default / kube-system / 自建项目空间。
- `Pod`：最小调度单元，封装 1~N 容器共享网络与存储。
- 控制器
  - `Deployment`：无状态应用，滚动升级，自动副本恢复。
  - `StatefulSet`：有状态应用，固定网络标识，按序滚动，常配合 `PVC`。
  - `DaemonSet`：每个节点 1 个 Pod（如日志采集、监控 Agent）。
  - `Job/CronJob`：一次性或周期性任务。
- 服务暴露
  - `Service`：内部稳定访问入口，类型有 `ClusterIP`（默认）、`NodePort`、`LoadBalancer`、`Headless`（无虚 IP，常配合 StatefulSet）。
  - `Ingress`：七层入口，按域名/路径转发到 Service。
- 配置与存储
  - `ConfigMap` / `Secret`：注入配置；Secret 默认 base64 编码，注意权限。
  - `Volume`：Pod 级存储接口；`emptyDir`、`hostPath`、`configMap` 等。
  - `PVC/PV/StorageClass`：声明式持久化存储，请求-绑定-提供者三层解耦。
- 调度与约束
  - `Label/Selector`：一切关联的基础；Service/Deployment/Ingress 都靠它匹配。
  - `nodeSelector` / `Node/Pod Affinity` / `Taint & Toleration`：控制 Pod 落在哪些节点。
  - `TopologySpreadConstraints`：让副本分布更均匀。
- 健康与生命周期
  - `livenessProbe` 重启挂掉的容器，`readinessProbe` 控制流量切换，`startupProbe` 给慢启动应用时间。
  - `initContainers` 用于准备依赖；`sidecar` 模式承载辅助能力（如日志、代理）。
- 资源与弹性
  - `requests/limits`：调度与限流依据；过载会触发 OOMKill/Throttle。
  - `HPA`：按 CPU/内存/自定义指标自动扩缩容。
- 权限与安全
  - `ServiceAccount` 代表工作负载身份；`Role/ClusterRole + Binding` 组成 RBAC。
  - `NetworkPolicy` 控制 Pod 间/入口的流量范围。

#### 核心对象详解（含命名由来）
- `Namespace`：集群里的逻辑分区，资源名在各自空间内唯一，方便隔离环境/团队；字面含义是“名字的作用域”。
- `Pod`：K8s 最小调度单元，容器共享网络/IP 和存储卷；取自“豆荚”，强调多个种子（容器）在一起。
- `Deployment`：声明期望副本数/镜像/策略的控制器，负责滚动升级、自愈；名字强调“部署”动作的声明式模板。
- `StatefulSet`：用于有状态服务，保持稳定身份（有序 Pod 名、固定存储绑定）；名字表示“有状态的集合”。
- `DaemonSet`：保证每个（或符合条件的）节点都运行一个 Pod，常用于日志/监控 Agent；名字意为守护进程集合。
- `Job/CronJob`：一次性或按 Cron 表达式周期运行的任务控制器；“Job”突出工作/任务，“CronJob”加入定时语义。

#### 核心对象使用要点
- `Namespace`
  - 用途：隔离环境/团队/项目，避免资源命名冲突；可配合配额、网络策略做“软多租”。
  - 命名缘由：表示“名字的作用域”，同名资源可以在不同命名空间共存。
  - 何时用：按环境（dev/stage/prod）或团队划分；系统组件保持在 kube-system。
- `Pod`
  - 用途：容器组合的最小调度单位，内部容器共享 IP 和存储卷；常见 sidecar（如日志/代理）与主容器并行。
  - 命名缘由：来自“豆荚”，强调多个种子紧密包裹在一起。
  - 何时用：一般不直接写 Pod，改用控制器（Deployment/StatefulSet/DaemonSet）来管理生命周期。
 
   - 用途：无状态应用首选，支持滚动升级、回滚、自愈副本。
  - 命名缘由：强调“部署模板”——声明期望状态，由控制器去实现。
  - 何时用：Web/API 等水平扩展的无状态场景；不负责有序启动或稳定网络标识。
- `StatefulSet`
  - 用途：有状态服务（数据库、队列）需要稳定网络身份、存储绑定、有序滚动。
  - 命名缘由：有状态（Stateful）的集合（Set）。
  - 何时用：需要固定主机名/PVC 绑定、按序升级/扩缩时；通常配合 Headless Service。
- `DaemonSet`
  - 用途：为每个节点（或满足 selector 的节点）部署一份 Pod，常见日志/监控/网络代理。
  - 命名缘由：守护进程（Daemon）的集合。
  - 何时用：节点级 Agent；不适合需要水平扩展的业务流量。
- `Job/CronJob`
  - 用途：一次性或按 Cron 表达式定时执行任务；可设置并发策略与重试。
  - 命名缘由：Job=任务；CronJob=基于 cron 的任务。
  - 何时用：数据清理、批处理、周期同步等；避免用 Deployment 跑定时任务。

### 3. `kubectl` 常用指令
- 查看：`kubectl get pod -n ns -o wide`，`kubectl describe pod xxx -n ns`，`kubectl get events -n ns --sort-by=.lastTimestamp`
- 日志/排错：`kubectl logs pod -c container -n ns`，`kubectl exec -it pod -n ns -- sh`，`kubectl port-forward pod/podname 8080:80`
- 部署与变更：`kubectl apply -f file.yaml`，`kubectl diff -f file.yaml`，`kubectl delete -f file.yaml`
- 升级与回滚（Deployment）：`kubectl rollout status deploy/xxx`，`kubectl rollout history deploy/xxx`，`kubectl rollout undo deploy/xxx`
- 查文档：`kubectl explain deploy.spec.template.spec.containers.livenessProbe`

### 4. 典型清单示例
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: demo
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
  namespace: demo
data:
  APP_ENV: "prod"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: demo
spec:
  replicas: 2
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
        - name: web
          image: nginx:1.25
          ports: [{containerPort: 80}]
          envFrom: [{configMapRef: {name: web-config}}]
          resources:
            requests: {cpu: "100m", memory: "128Mi"}
            limits: {cpu: "500m", memory: "256Mi"}
          readinessProbe:
            httpGet: {path: /, port: 80}
            initialDelaySeconds: 3
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: demo
spec:
  type: ClusterIP
  selector: {app: web}
  ports:
    - port: 80
      targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  namespace: demo
spec:
  ingressClassName: nginx
  rules:
    - host: web.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port: {number: 80}
```

### 5. 常见排错思路
- 先看 `kubectl get pod -w` 是否在 Running；Pending 查看 `kubectl describe pod` 中的调度/镜像/拉取错误。
- CrashLoopBackOff：用 `kubectl logs --previous` 看上一次启动日志，结合 liveness/readiness 设定是否过严。
- 无法访问：检查 Service `selector` 是否匹配 Pod 标签，`Endpoints` 是否为空，Ingress 规则与证书是否正确。
- 性能/限流：确认 `requests/limits`，通过 `kubectl top pod`（需 metrics-server）或监控指标观察瓶颈。
- 权限：若报 RBAC 拒绝，检查 Pod 使用的 `serviceAccountName` 及绑定的 Role。

### 6. 实践路径（建议按顺序动手）
1) 本地或远端准备集群（kind/minikube/托管 K8s），配置好 kubeconfig。
2) 创建命名空间，部署上方示例，验证 `kubectl get all -n demo` 正常。
3) 修改镜像版本触发滚动升级；体验 `rollout history/undo`。
4) 增加 `HPA` 并压测验证自动扩缩容。
5) 给 Deployment 挂 `PVC`，尝试 `StatefulSet` + `Headless Service` 观察稳定网络标识。
6) 配置简单 `NetworkPolicy`，只允许 Ingress/Service 进流量，验证拒绝未授权 Pod。
7) 结合日志与监控组件（如 Loki/Prometheus）做一次排错演练。

### 7. 进阶方向
- Helm/Operator：用 Helm 管理多环境发布，用 Operator 自动化有状态业务。
- GitOps：Argo CD/Flux 以 Git 为唯一事实源。
- 安全：镜像签名与扫描（cosign/trivy）、Pod Security Standard、密钥管理（KMS）。
- 可观测性：指标 + 日志 + Trace（OpenTelemetry）三件套。

> 提示：随时用 `kubectl explain` 看字段含义，配合 `kubectl diff` 确认变更，保持“声明式 + 小步快跑”的节奏。
