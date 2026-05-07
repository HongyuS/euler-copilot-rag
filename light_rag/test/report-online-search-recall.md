# online-search 召回率评测报告

- 评测时间: 2026-04-29 11:11:24
- 总样本数: 45
- 平均延迟: 6646.57 ms

## Recall

| 类型 | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
| --- | --- | --- | --- | --- |
| issue | 0.1429 | 0.1429 | 0.1429 | 0.1429 |
| commit | 0.0000 | 0.0417 | 0.0417 | 0.0417 |
| overall | 0.0667 | 0.0889 | 0.0889 | 0.0889 |

## 未命中样本（最多展示20条）

- 1. [issue] `cri pinned label never applied pinned_images config value`
  - repo: `containerd/containerd`
  - latency_ms: `6442.99`
  - top_returned: ["Proposal: Update labels ", "Forward service labels to OCI spec for cgroup resource controls (blockIO, unified)", "Docker with containerd-snapshotter does not support client certificates for registry authentication", "[Branch status] (master -> next release: v29.5.X), (cherry pick 🍒 ⛏  docker-29.x -> 29.4 patch release)", "Pending task never goes away", "Allow overrides of the default base OCI spec ", "Swarm service does not rollout when --resolve-image never is used", "[RFE] Support for OCI hooks [2018 edition]", "new security-opt: privileged-without-host-devices", "SELinux options user/role/type break pod-wide SELinux level"]
- 2. [issue] `ctr image export by digest reference creates an`
  - repo: `containerd/containerd`
  - latency_ms: `6789.27`
  - top_returned: ["Images with sha512 layers are not usable", "Docker save is not exporting image tag when image is referenced by ID", "`docker save` with containerd snapshotter returns OCI images missing all blob layers when image shares layers with another image", "docker image ls does not show images loaded from a tar file", "c8d: `buildx build`, `load`, and `import` don't preserve dangling image", "containerd image store: Layer content not pulled if a snapshot exists", "docker pull fails with \"content digest not found\" when using containerd snapshotter (works with containerd-snapshotter=false)", "Docker v29 pulls all architecture variants of a multi-arch image by default and changes image ID semantics, causing increased disk usage and breaking existing tooling", "Proposal: c8d: expose contentstore API", "Pulling an image with `application/octet-stream` config media type fails"]
- 3. [issue] `proposal cross image layer deduplication overlay snapshotter`
  - repo: `containerd/containerd`
  - latency_ms: `6526.99`
  - top_returned: ["Proposal: Global Image/Layer Namespace", "[Proposal]: docker diff between image layers", "Proposal: refactor image management code", "Proposal: Docker Volume Layer 'docker run --volume-layer'", "`docker save` with containerd snapshotter returns OCI images missing all blob layers when image shares layers with another image", "Proposal: c8d: expose contentstore API", "Proposal: Filesystem integrity check", "partial layer/image export", "Cannot safely remove dangling image layers from Windows Images", "Proposal: Add --from support to ADD command"]
- 4. [issue] `color flag instead of only having systemd_colors since`
  - repo: `systemd/systemd`
  - latency_ms: `6607.6`
  - top_returned: ["c8d: docker push discards platform variants instead of erroring", "cpu-percent flag only applies to main process", "Subsequent COPY instructions re-adds all files in every layer instead of only the files that have changed", "Multiple tcp syn after some network inactivity", "Ability to mount cgroupfs as read/write with `--cgroupns=private`", "docker ps -v for verbose info: PID and namespace", "\"docker info\" inside dind shows host memory instead of container memory", "overlay nw: TCP PSH after >60s sleep leads to TCP RST (seems swarm-mode only)", "build time only -v / --volume option", "The mount flags of \"_netdev\" can not be copied from container to the host"]
- 5. [issue] `defaulttimeoutstopsec is working or sometimes working`
  - repo: `systemd/systemd`
  - latency_ms: `7454.38`
  - top_returned: ["vendor validation not working correctly", "dnsrr endpoint mode not working with routing mesh", "GET /volumes : dangling filters not working as expected", "nslookup container hostname not working (Win2019, gMSA)", "Swarm Network Encryption stopped Working after Upgrade", "Service network alias not working for services created using stack deploy on 1.13", "Docker swarm load balancing not working over private network", "\"chmod 555 /\" within docker build not working correctly", "Server 2016 Container stops working after windows update", "Docker bridge network leaks internal IP addresses (masquerade not working)"]
- 6. [issue] `varlink enable disable unit`
  - repo: `systemd/systemd`
  - latency_ms: `6444.56`
  - top_returned: ["Disable Userland proxy by default", "No option to disable IPv4 on default Docker bridge", "testing: (fix, and) enable more Attach tests on Windows", "'ip_forward' is disabled in the load balancer network namespace", "Cannot disable/remove a volume plugin", "Unable to build a simple Dockerfile with buildx where userns-remap and the containerd backend is enabled", "Docker Network bypasses Firewall, no option to disable", "BUG!? - Cores affinity with --cpuset-cpus works only one way (disable works, enable not)", "Using docker build in rootless mode ", "Docker swarm init does not enable ipv6 networking even with ipv6 listening address"]
- 7. [issue] `opportunisticbatching try batch hint as fallback nominatednodename is`
  - repo: `kubernetes/kubernetes`
  - latency_ms: `5900.36`
  - top_returned: ["UX: improve / design UX for multi-arch images", "Splunk Driver Bug", "Docker login only tries v1 URI", "Slow networking inside containers (tried host and bridge)", "Docker Rootless on diskless compute nodes Slirp4netns Issuse", "attach websocket close as soon as opened", "Not able to use container as gateway in internal network", "Unable to install Go SDK", "`id` command cannot show correct *secondary* group information inside container with mounted /etc/group and /etc/passwd files", "Docker help isn't as helpful anymore w.r.t. options"]
- 8. [issue] `node log query unexpected result disabled`
  - repo: `kubernetes/kubernetes`
  - latency_ms: `6775.27`
  - top_returned: ["swarm:Two nodes have the same node ID", "Ringlogger (non-blocking logs) drops messages if underlying logger fails", "output buffering or timestamp granularity issue (log lines in the wrong order)", "Use node label in log opt tag? ", "bind mount unexpectedly follows symlink", "Bind-mounting with subdirectories inside read-only mounted volume gives unexpected error", "Filtering nodes doesn't return a result", "[Windows Server 2019] Unexpected backspaces in tty output", "`docker service logs` stops showing logs from containers on different nodes", "Symlinks in directories are not resolved when using --device"]
- 9. [issue] `inconsistent finalizer validation across built in resources`
  - repo: `kubernetes/kubernetes`
  - latency_ms: `7064.25`
  - top_returned: ["Docket Network Naming Requirement  Inconsistent with Error Message", "Swarm overlay IPv6 subnet cannot be allocated (invalid Prefix / inconsistent pool handling) in Docker 29.4.1", "Inconsistent --publish behavior", "Inconsistent behaviour of masquerade / proxy", "make it easier to diagnose firewall misconfigurations blocking overlay network data path", "tmpfs mount’s mode inconsistency", "Windows container - inconsistent interactive prompt behaviour", "Proc connector across pid namespace - a security issue?", "API swagger doc for `Topology` inconsistent with Go implementation", "Inconsistent uname output between docker build and docker run"]
- 10. [issue] `add new member one member is down even`
  - repo: `etcd-io/etcd`
  - latency_ms: `6617.59`
  - top_returned: ["Make service network alias support templating", "Using healthcheck on swarm disturbs nameservices", "Add option to print swarm's load balancer pool members for a Docker service", "dockerfile FROM should deny the usage of a digest that does not match the tag", "\"Misleading\" output of docker swarm join-token", "Possibility to add support for running containers under Android (GOOS=android)", "Non-default user is not added to LOCAL group (S-1-2-0) ", "Swarm level metadata", "swarm node suddenly went down after \"Decrypt packet failed\" warning (18.06.0-ce)", "testing: runconfig: add new fixtures to TestDecodeContainerConfig"]
- 11. [issue] `rejected connection eof using etcdctl multiple endpoints`
  - repo: `etcd-io/etcd`
  - latency_ms: `6756.32`
  - top_returned: ["Tracking issue for health start interval", "FromEnv should work with an SSH transport set via DOCKER_HOST", "AppArmor policy to deny network is not working", "API should either reject, de-duplicate, or warn duplicate exposed-ports ", "[RFC]: remove uses of github.com/docker/go-connections/tlsconfig defaults", "Resumable uploads to the registry", "Creating container on Windows Server 2022 fails with transparent network - EOF: 125", "Calling HijackResponse.CloseWrite from ContainerAttach causes EOF on read side too", "Rootless with slirp4netns and TCP Certificate dont work", "Cannot start container: Getting the final child's pid from pipe caused \"EOF\""]
- 12. [issue] `tool improve benchmark tool`
  - repo: `etcd-io/etcd`
  - latency_ms: `6395.12`
  - top_returned: ["Make the log lines splitting configurable", "Improve swarm mode for automated setup", "Improve usability for TLS usage and setup", "Improve usage for commands", "allow setting a default architecture platform for running containers with orchestration tools", "UX: improve / design UX for multi-arch images", "hcsshim::ImportLayer failed after cygwin and vs2015 build tools installations", "Global .dockerignore", "Improving doc about Limit-Cpu for docker engine in swarm mode", "client.FromEnv TLS config is not consistent with the command line tool"]
- 13. [issue] `flaky test runc run cgroup v2 resources unified`
  - repo: `opencontainers/runc`
  - latency_ms: `6795.17`
  - top_returned: ["Flaky test: TestRestartDaemonWithRestartingContainer", "Systemctl daemon-reload reset docker container cgroup", "Flaky test: TestDaemonHostGatewayIP", "Flaky test: TestUserChain (libnetwork)", "Validate runc 1.4 pids.limit breaking change does not affect spec generation", "Flaky test: TestRunPIDsLimit", "Flaky test: TestFindNetworkUtil (lib network)", "context canceled during large image export on Docker 29.1.3 + containerd 2.2.1 causing ref lock", "Improve documentation for custom cgroups (--cgroup-parent)", "Symlinks in directories are not resolved when using --device"]
- 14. [issue] `runc features runc expose libpathrs version`
  - repo: `opencontainers/runc`
  - latency_ms: `7026.47`
  - top_returned: ["context canceled during large image export on Docker 29.1.3 + containerd 2.2.1 causing ref lock", "Un-provide runc", "docker pull fails with \"content digest not found\" when using containerd snapshotter (works with containerd-snapshotter=false)", "Docker info reports incorrect runc version if default runtime is not runc", "API should either reject, de-duplicate, or warn duplicate exposed-ports ", "Add umask configuration into runc", "`--gpus all` does not expose MIG devices in Docker 29.2.0", "Symlinks in directories are not resolved when using --device", "Use of root cgroup v2 yields missing features", "Validate runc 1.4 pids.limit breaking change does not affect spec generation"]
- 15. [issue] `runc selinux library use cpu`
  - repo: `opencontainers/runc`
  - latency_ms: `6439.89`
  - top_returned: ["docker pull fails with \"content digest not found\" when using containerd snapshotter (works with containerd-snapshotter=false)", "Enable SELinux support for overlay2 in rootless mode", "Symlinks in directories are not resolved when using --device", "SELinux options user/role/type break pod-wide SELinux level", "SELinux is preventing chown from setattr access on the fifo_file .", "lsetxattr /dev/mqueue operation not permitted when using docker userns with selinux-enabled", "Memory leak in dockerd when container exceeds its --memory limit and has a low OOM score", "Add CPU hotplug support", "Docker container image BTRFS subvolumes created without a root context on SELinux systems", "CONTAINER_PARTIAL_LAST is always false"]
- 16. [issue] `cri v1 regression handling crictl request`
  - repo: `cri-o/cri-o`
  - latency_ms: `7302.23`
  - top_returned: ["Docker with containerd-snapshotter does not support client certificates for registry authentication", "registry-mirror regression with containerd storage", "Improve handling of hybrid v1/v2 cgroups", "Mount OCI Artifacts", "When using containerd-snapshotter, the insecure-registries setting does not work", "Swarm overlay IPv6 subnet cannot be allocated (invalid Prefix / inconsistent pool handling) in Docker 29.4.1", "Daemon logs missing useful information (regression)", "Regression: Service image no longer pinned by hash in API v1.26", "Attempting to use containerd-snapshotter mode with nix-snapshotter", "non-host container restart will change ths resolv"]
- 17. [issue] `nri stopsandbox hook network namesapces`
  - repo: `cri-o/cri-o`
  - latency_ms: `6165.38`
  - top_returned: ["NRI: Container state", "[Epic] Node Resource Interface (NRI)", "NRI: Container lifecycle", "NRI: User docs", "NRI: Container updates", "NRI: Configuration options", "Attached Networks are missing in \"poststart\" hook >= 28", "NRI: Container adjustment on create", "NRI: Pod lifecycle and state", "containerdexecutor: add network namespace callback follow-ups"]
- 18. [issue] `cri sends multiple accept headers pulling images`
  - repo: `cri-o/cri-o`
  - latency_ms: `7125.3`
  - top_returned: ["Docker with containerd-snapshotter does not support client certificates for registry authentication", "Very slow download speed when fetching 'tar' from container with encoding headers", "allow docker cp to accept several different folders", "[RFE] Support for OCI hooks [2018 edition]", "c8d: allow pulling images for multiple architectures", "Cannot receive UDP traffic in Docker container in case of UDP server being located at Docker host", "Windows Swarm multiple overlay network DNS resolution issues", "new security-opt: privileged-without-host-devices", "How can send udp broadcast on docker images.", "Mount OCI Artifacts"]
- 19. [commit] `docs cgroup typo protetion protection small typo in`
  - repo: `torvalds/linux`
  - latency_ms: `6172.63`
  - top_returned: ["mm: memcontrol: remove dead code of checking parent memory c", "rust: pin-init: implement ZeroableOption for NonZero* intege", "cgroup/cpuset: Call rebuild_sched_domains() directly in hotp", "drm/xe/uapi: Define drm_xe_vm_get_property\n\nAdd initial decl", "mm/damon: add DAMOS quota goal type for per-memcg per-node m", "Merge tag 'bpf-next-7.1' of git://git.kernel.org/pub/scm/lin", "Merge tag 'wq-for-7.1' of git://git.kernel.org/pub/scm/linux", "Merge tag 'mm-stable-2026-04-18-02-14' of git://git.kernel.o", "arm64: dts: imx8mm-emtop-som: Correct PAD settings for PMIC_", "ACPICA: Update the format of Arg3 of _DSM\n\nTo get rid of typ"]
- 20. [commit] `docs isofs replace dead ecma ftp link original`
  - repo: `torvalds/linux`
  - latency_ms: `6806.08`
  - top_returned: ["btrfs: replace kcalloc() calls to kzalloc_objs()\n\nCommit 293", "linux/bitfield.h: replace __auto_type with auto\n\nReplace \"__", "drm/xe/uapi: Define drm_xe_vm_get_property\n\nAdd initial decl", "Merge tag 'rust-7.1' of git://git.kernel.org/pub/scm/linux/k", "RDMA: Complete k[z|m|c]alloc-to-k[z|m]alloc_obj conversion\n\n", "Merge tag 'bpf-next-7.1' of git://git.kernel.org/pub/scm/lin", "PCI: Validate window resource type in pbus_select_window_for", "rust: pin-init: implement ZeroableOption for NonZero* intege", "slab.h: disable completely broken overflow handling in flex ", "Merge tag 'staging-7.1-rc1' of git://git.kernel.org/pub/scm/"]