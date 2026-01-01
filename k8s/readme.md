# 核心概念
各大资源对象的最佳实践
熟练运用k8s各项调度策略
掌握k8s网络原理及应用
数量掌握pod控制器及运用场景
数量掌握k8s微服务devops实践



1. 命名空间级
    工作负载类型
    服务器发现与负载均衡
    配置与存储
    特殊类型存储
    其他 

搭建 
二进制

生命周期

deployment

statefulset 有状态应用

daemonset 
持久化存储  有状态的存储比如说数据库

高级调度
    亲和力
    污点与容忍
    初始化容器

身份与权限认证
    认证与授权

helm 包管理器
    chart
集群监控
    监控方案

日志管理

可视化界面


容器： 实现文件系统  网络 cpu 内存 磁盘 进程  用户空间等资源的隔离


k8s的特点 自我修复  弹性伸缩  自动化部署与回滚 服务发现与负载均衡  存储编排 配置与密钥集中管理 多环境一致性与可移植性 批处理与定时任务支持

集群架构与组件
    控制面板
        kube-apiserver 核心入口  所有组件都通过它与集群交互 提供restful api
        kube-controller-manager 运行多个控制器，确保集群实际状态与期望状态一致  
        创建的控制器 
            node controller 检测node 是否宕机  
            reoplication controller 维持pod副本数 现在都用replicaSet
            endpoint controller  维护service 与pod的映射
            service Account & token controller 自动创建默认的serivceaccount 和api token
        kube-scheduler 负责将新创建的pod调度到合适的worker node上 调度的依据是 资源需求  亲和、反亲和  污点taint  容忍 toleration  
        etcd  分布式键值数据库，保存集群的全部状态数据 比如pod丁一 service 配置  node状态
    节点
        kubelet 负责与api server通信 不管理非k8s创建的容器
            确保本机上的pod和容器按照spec正常运行
            执行检查 liveness readiness probes 上报node、pod状态
        kube-proxy  实现service的网络代理和负载均衡
            维护node上的网络规划ipvs或者ipteables 讲流量转发到后端pod
            支持clusterIP NodePort loadBalancer 等service

        container runtime 负责运行容器的实际引擎
            通过 CRI container runtime interface 接口集成

        
    附加
        kube-dns
        ingress controller
        heapster
        dashboard


组件	职责简述
kube-apiserver	集群 API 入口，唯一操作 etcd 的组件
etcd	存储集群所有状态
kube-scheduler	决定 Pod 跑在哪台机器
kube-controller-manager	自动修复集群状态（如补副本、删孤儿 Pod）
kubelet	管理本机 Pod 和容器
kube-proxy	实现 Service 网络代理
Container Runtime	实际运行容器的引擎

用户-->API server ->etcd 存状态--> controller盯状态+schduler 分配任务-->work node （kubelet执行+ kube-proxy转发）


服务的分类
    状态 = 应用运行过程中产生的、需要持久化或跨请求保持的数据。
    有状态
    有状态服务（Stateful Service） statefulset

        依赖持久化数据或唯一身份标识。
        实例之间不对等：每个实例有稳定、唯一的网络标识和专属存储。
        扩缩容需按顺序（如先启 pod-0，再 pod-1）。
        删除后重建必须保留原身份和数据。    
    无状态 不保存任何与特定用户或请求相关的持久数据  deployment
        不保存客户端上下文，每次请求都独立处理。
        所有实例完全对等（identical），可任意扩缩容、替换、重启。
        可以轻松水平扩展（Scale Out）。
        故障恢复简单：直接启动新实例即可。

尽可能无状态，必要时才引入状态

k8s所有内容都是资源
对象是资源的实例
spec  规约  specification   是用户定义的期望状态
spec 可以嵌套！Deployment 的 spec 中包含了一个 Pod 模板，而该模板又有自己的 spec。
字段	含义	谁负责写入？
spec	期望状态（Desired State）	用户（通过 YAML 或 kubectl）
status	实际状态（Actual State）	Kubernetes 系统（自动更新）
资源分类  
    元数据类型
        hpa  horizontal pod autoscaler 自动伸缩
        podtemplate  
        limitrange
    集群 
        namespace
        node 
        
    命名空间

一个集群可以包含多个命名空间；
一个命名空间只属于一个集群；
命名空间是实现多项目、多团队、多环境共用集群的最佳实践；
但关键业务或高安全要求场景，仍建议使用独立集群。


资源类型	spec 中的关键内容
Pod	containers, volumes, restartPolicy, nodeSelector
Deployment	replicas, selector, template（Pod 模板）
Service	type, ports, selector（匹配后端 Pod）
StatefulSet	serviceName, replicas, volumeClaimTemplates
ConfigMap	data 或 binaryData（配置内容）
PersistentVolumeClaim	accessModes, resources.requests.storage

pause 实现2个容器之间共享
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: shared-pod
spec:
  containers:
  - name: writer
    image: busybox
    command: ["/bin/sh", "-c"]
    args:
      - |
        while true; do
          echo "$(date): Hello from writer" >> /shared/message.log
          sleep 5
        done
    volumeMounts:
    - name: shared-volume
      mountPath: /shared

  - name: reader
    image: busybox
    command: ["/bin/sh", "-c"]
    args:
      - |
        tail -f /shared/message.log
    volumeMounts:
    - name: shared-volume
      mountPath: /shared

  # 定义共享的 emptyDir 卷
  volumes:
  - name: shared-volume
    emptyDir: {}
```

副本 replicas
控制器
    无状态 
        replicationController RC
        replicaSet RS label selector 
        Deployment 
            创建RS/pod
            滚动升级、回滚
            暂停与恢复

    有状态
        StatefulSet
                顺序固定 

            headless service 对于有状态服务的dns管理  服务名--访问路径--ip
            volumeClaimsTemplate  

    守护进程
        DaemonSet
            所有匹配的到pod都部署一个守护进程 比如日志 监控 fluentd logstash  prometheus node export collected 
    任务/定时任务
        Job
        CronJob
    
服务发现
    service 集群内部
        核心作用：为一组具有相同功能的 Pod 提供固定访问地址和负载均衡能力，解决 Pod 动态漂移（IP 变化、销毁重建）导致的访问不稳定问题。
        定位：集群内服务发现与负载均衡的核心组件，默认仅在集群内可访问（除 NodePort/LoadBalancer 类型外）。
    ingress 外部进入流量 
        反向代理 负载均衡
        核心作用：作为集群外流量的统一入口，实现基于 HTTP/HTTPS 协议的路径路由、域名转发、SSL 终止等高级功能。
        定位：7 层 HTTP 路由转发器，依赖 Ingress Controller（如 Nginx Ingress、Traefik）才能工作，本身只是一个路由规则定义。
    特性	Service	Ingress
协议层级	4 层（TCP/UDP/SCTP）	7 层（HTTP/HTTPS）
访问范围	集群内（默认）或集群外（NodePort/LoadBalancer）	集群外（通过 Ingress Controller 暴露）
核心功能	Pod 负载均衡、服务发现、IP 固定	域名 / 路径路由、SSL 终止、7 层转发
依赖组件	无，Kubernetes 原生支持	必须部署 Ingress Controller（如 Nginx Ingress）
配置复杂度	简单，仅需定义端口和标签选择器	复杂，需定义域名、路径、证书等规则
负载均衡粒度	基于 IP + 端口，无路径 / 域名区分	基于域名 + 路径，支持细粒度路由
1. 仅用 Service 的场景
集群内 Pod 之间的通信（如前端 Pod 访问后端 API Pod），使用 ClusterIP 类型 Service。
需要直接暴露服务到集群外，且无需 7 层路由（如数据库、缓存服务），使用 NodePort 或 LoadBalancer 类型 Service。
分布式服务需要自主发现 Pod IP（如 Kafka、ZooKeeper），使用 Headless Service。
2. 必须用 Ingress 的场景
多个 HTTP 服务需要通过同一个 IP / 域名暴露到集群外（如 example.com/api 对应后端 API，example.com/web 对应前端页面）。
需要支持 HTTPS 访问，且希望统一管理 SSL 证书（避免每个 Service 单独配置证书）。
需要基于域名路由（如 api.example.com 对应 API 服务，admin.example.com 对应管理后台）。

配置与存储
    volume
    csi 暴露容器内存储    
pv对运维
pvc对开发

特殊类型配置
    configMap
    Secret
    DownardAPI

其他
    role
    roleBinding



    

1. 集群外机器管理k8s
    下载kubectl+kubeconfig的方式
kubectl
    创建对象
    显示和查找资源
    修补资源
    编辑资源
    scale资源

默认命名空间default

比如kubectl get pods  得到2个

luo@luo-u2403:~$ kubectl get pods
NAME                            READY   STATUS    RESTARTS      AGE
nginx-deploy-77bf8679f9-5stmr   1/1     Running   0             16d
nginx-deploy-77bf8679f9-l9l9c   1/1     Running   2 (16d ago)   24d
# 现获取到它的deploy信息
luo@luo-u2403:~$ kubectl get deploy
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deploy   2/2     2            2           24d

# 然后开始scale
需要填写对应的deployment信息
luo@luo-u2403:~$ kubectl scale deploy --replicas=3
error: resource(s) were provided, but no name was specified
luo@luo-u2403:~$
luo@luo-u2403:~$ kubectl scale deploy --replicas=3 nginx-deploy
deployment.apps/nginx-deploy scaled
luo@luo-u2403:~$
luo@luo-u2403:~$ kubectl get deploy
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deploy   3/3     3            3           24d

kubectl get pod -o wide
# 获取信息成yaml
luo@luo-u2403:~$ kubectl get deploy nginx-deploy -oyaml
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "1"
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"nginx-deploy","namespace":"default"},"spec":{"replicas":2,"selector":{"matchLabels":{"app":"nginx"}},"template":{"metadata":{"labels":{"app":"nginx"}},"spec":{"containers":[{"image":"nginx:1.25","name":"nginx","ports":[{"containerPort":80}]}]}}}}
  creationTimestamp: "2025-12-08T01:56:09Z"
  generation: 3
  name: nginx-deploy
  namespace: default
  resourceVersion: "7520094"
  uid: 744f39cc-fcdf-493b-a243-80b7aba6bd6b
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: nginx
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx:1.25
        imagePullPolicy: IfNotPresent
        name: nginx
        ports:
        - containerPort: 80
          protocol: TCP
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
status:
  availableReplicas: 1
  conditions:
  - lastTransitionTime: "2025-12-08T01:56:09Z"
    lastUpdateTime: "2025-12-08T01:56:11Z"
    message: ReplicaSet "nginx-deploy-77bf8679f9" has successfully progressed.
    reason: NewReplicaSetAvailable
    status: "True"
    type: Progressing
  - lastTransitionTime: "2026-01-01T08:25:17Z"
    lastUpdateTime: "2026-01-01T08:25:17Z"
    message: Deployment has minimum availability.
    reason: MinimumReplicasAvailable
    status: "True"
    type: Available
  observedGeneration: 3
  readyReplicas: 1
  replicas: 1
  updatedReplicas: 1


api
    类型
        alpha
        beta
        stable
    访问控制
        认证
        授权

对pod进行操作
