#include <iostream>
#include <liburing.h>
#include <unistd.h>
#include <thread>
#include <sched.h>
#include "keystone_spsc_queue.h"

/**
 * KEYSTONE KERNEL BYPASS (v4.0): The 'No-Limits' Pipe
 * Purpose: Eliminate remaining hardware/OS limitations via:
 * 1. CPU Pinning: Bind threads to dedicated physical cores (Isolate from Scheduler).
 * 2. Busy-Polling: Remove 'yield' and 'sleep' to achieve nanosecond response.
 * 3. SQPOLL + Zero-Copy: Already implemented, now maximized.
 */

struct TelemetryEvent {
    char data[128];
    size_t length;
};

// Global queue for the pipeline
KeystoneSPSCQueue<TelemetryEvent, 1024> pipeline_queue;

// Helper to pin thread to a specific CPU core
void pin_thread_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        std::cerr << "⚠️ Failed to pin thread to core " << core_id << std::endl;
    } else {
        std::cout << "📍 Thread pinned to Core " << core_id << std::endl;
    }
}

// Task: The Reaper/Ingestor (Consumer) - Pins to Core 1
void io_uring_worker() {
    pin_thread_to_core(1);
    
    struct io_uring ring;
    struct io_uring_params params;
    memset(&params, 0, sizeof(params));
    params.flags = IORING_SETUP_SQPOLL;
    params.sq_thread_idle = 10000; // Keep kernel thread alive for 10s

    if (io_uring_queue_init_params(256, &ring, &params) < 0) {
        io_uring_queue_init(256, &ring, 0);
    }

    while (true) {
        auto event = pipeline_queue.pop();
        if (event) {
            struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
            if (sqe) {
                struct iovec iov;
                iov.iov_base = (void*)event->data;
                iov.iov_len = event->length;
                io_uring_prep_writev(sqe, STDOUT_FILENO, &iov, 1, 0);
                io_uring_submit(&ring);
            }
        }
        // ELIMINATED: std::this_thread::yield() - We now BUSY-POLL for absolute zero latency.
        
        struct io_uring_cqe *cqe;
        while (io_uring_peek_cqe(&ring, &cqe) == 0) {
            io_uring_cqe_seen(&ring, cqe);
        }
    }
}

int main() {
    std::cout << "🚀 Initializing Keystone Kernel Bypass v4.0..." << std::endl;
    
    // Pin the main 'Muscle' thread to Core 0
    pin_thread_to_core(0);

    std::thread ingest_thread(io_uring_worker);

    // Main 'Muscle' thread: Push data with zero waiting
    for (int i = 0; i < 5; ++i) {
        TelemetryEvent ev;
        ev.length = snprintf(ev.data, 128, "{\"id\": %d, \"status\": \"BYPASS_ACTIVE\"}\n", i);
        // BUSY-WAIT: Spin until the queue has space
        while (!pipeline_queue.push(ev)); 
    }

    ingest_thread.detach();
    sleep(1); 
    return 0;
}
