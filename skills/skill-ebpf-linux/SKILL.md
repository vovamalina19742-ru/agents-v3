---
name: skill-ebpf-linux
description: eBPF Linux Kernel Tracing & Low-Level Observability Guide for real-time process monitoring, network packet inspection, and performance profiling.
---

# eBPF Linux Kernel Tracing & Observability (`skill-ebpf-linux`)

## Overview
This skill provides low-level Linux kernel observability and tracing patterns derived from *«Изучаем eBPF»* and *«Ядро Linux: Сборка, настройка, управление (2023)»*.

---

## ⚡ 1. Core Architecture Principles

- **Zero Kernel Modification:** Attach custom BPF bytecode programs directly to kernel kprobes, tracepoints, and XDP (eXpress Data Path) hooks without recompiling the Linux kernel.
- **In-Kernel Verification:** All eBPF programs pass the static kernel verifier to guarantee memory safety and prevent kernel panics.

---

## 🛠 2. Essential `bpftrace` One-Liners

### Process Execution Tracing
Trace all new process executions (`execve` syscalls):
```bash
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("%s -> %s\n", comm, str(args->filename)); }'
```

### Disk I/O Latency Profiling
Measure block I/O latency distribution:
```bash
bpftrace -e 'kprobe:vfs_read { @start[tid] = nsecs; } kretprobe:vfs_read /@start[tid]/ { @ns = hist(nsecs - @start[tid]); delete(@start[tid]); }'
```

### Network Socket Connections
Trace TCP connect attempts across network sockets:
```bash
bpftrace -e 'kprobe:tcp_v4_connect { $sk = (struct sock *)arg0; printf("PID %d (%s) connecting...\n", pid, comm); }'
```

---

## 🚀 3. Integration with Telemetry (Fluent Bit)
- Stream eBPF trace logs directly to **Fluent Bit** over Unix Domain Sockets or HTTP for ultra-low memory (1-3 MB RAM) AgentOps tracing.
