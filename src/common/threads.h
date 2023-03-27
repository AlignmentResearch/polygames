#pragma once

#include <string>
#include <iostream>
#include <vector>
#include <queue>
#include <functional>
#include <thread>
#include <mutex>
#include <condition_variable>

namespace threads {

class Threads {
    /* Singleton that holds the threads for the whole duration of the program. It takes functions from each thread's
     * queue and runs them. */
public:
    void enqueue(std::shared_ptr<std::function<void()>> f_ptr, size_t threadID);

    static void init(size_t nThreads);
    static Threads& inst();

    Threads(const Threads&) = delete;
    Threads& operator=(const Threads&) = delete;

    Threads(Threads&&) = delete;
    Threads& operator=(Threads&&) = delete;

    size_t getNumThreads() { return numThreads; }

    friend std::default_delete<Threads>;  // Allow unique_ptr to delete this
private:
    Threads(size_t nThreads);
    ~Threads();

    static std::unique_ptr<Threads> instance;

    size_t numThreads;
    std::vector<std::thread> threads;
    std::vector<std::queue<std::shared_ptr<std::function<void()>>>> functionQueue;
    std::mutex queueMutex;
    std::condition_variable condition;
    bool terminate = false;
    void threadLoop(size_t threadID);
};

class Task {
    /* A collection of functions to run in parallel, and utilities to enqueue them in Threads and wait for all of them
     * to finish. */
public:
    void push_back(std::function<void()> f);
    void enqueue_all(Threads &threads);
    void wait();
    void check_not_running();
    void clear();

private:
    std::mutex m_functions_mutex;
    std::vector<std::shared_ptr<std::function<void()>>> m_functions;

    size_t m_numRunning = 0;
    std::mutex m_running_mutex;
    std::condition_variable m_condVar;
};

void setCurrentThreadName(const std::string& name);

}  // namespace threads
