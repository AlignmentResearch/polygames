#include "threads.h"

#include <iostream>
#include <stdexcept>
#include <cassert>

namespace threads {


std::mutex Threads::instanceMutex;
std::unique_ptr<Threads> Threads::instance = nullptr;

void Threads::init(size_t nThreads) {
    if (nThreads <= 0) {
      nThreads = std::thread::hardware_concurrency();
      if (nThreads <= 0) {
        throw std::runtime_error("Could not automatically determine the "
                                  "number of hardware threads :(");
      }
      std::cout << "Starting " << nThreads << "threads (automatically configured)" << std::endl;
    } else {
      std::cout << "Starting " << nThreads << "threads" << std::endl;
    }

    std::unique_lock lock(instanceMutex);
    if (!instance) {
        // using new is a bit bad, but unique_ptr cannot call the private constructor.
        instance = std::make_unique<Threads>(nThreads);
    } else {
        if (instance->numThreads != nThreads) {
	  std::cerr << "WARNING: Number of threads already set to " << instance->numThreads
              << ", requested: " << nThreads << ". Ignoring request." << std::endl;
        }

    }
}

Threads& Threads::inst() {
    std::unique_lock lock(instanceMutex);
    if (!instance) {
        throw std::logic_error("Singleton instance not initialized");
    }
    return *instance;
}


Threads::Threads(size_t nThreads) : numThreads(nThreads), threads(nThreads), functionQueue(nThreads) {
    for (size_t i = 0; i < numThreads; i++) {
        threads.at(i) = std::thread(&Threads::threadLoop, this, i);
    }
}

Threads::~Threads() {
    {
        std::lock_guard<std::mutex> lock(queueMutex);
        terminate = true;
    }
    condition.notify_all();
    for (auto& thread : threads) {
        thread.join();
    }
}

void Threads::enqueue(std::shared_ptr<std::function<void()>> f_ptr, size_t threadID) {
  assert(f_ptr != nullptr);
  {
      std::lock_guard<std::mutex> lock(queueMutex);
      functionQueue.at(threadID).push(std::move(f_ptr));
  }
  condition.notify_all();
}

void Threads::threadLoop(size_t threadID) {
    setCurrentThreadName("async " + std::to_string(threadID));
    while (true) {
        std::unique_lock<std::mutex> lock(queueMutex);
        condition.wait(lock, [this, threadID]() { return terminate || !functionQueue.at(threadID).empty(); });
        if (terminate) {
            break;
        }
        std::shared_ptr<std::function<void()>> function = functionQueue.at(threadID).front();
        functionQueue.at(threadID).pop();

        lock.unlock();
        (*function)();
    }
}

void setCurrentThreadName(const std::string& name) {
#ifdef __APPLE__
  pthread_setname_np(name.c_str());
#elif __linux__
  pthread_setname_np(pthread_self(), name.c_str());
#endif
}

void Task::check_not_running() {
  std::unique_lock<std::mutex> lock(m_running_mutex);
  if(m_numRunning > 0) {
    throw std::logic_error("Some functions from this task are already running, cannot enqueue");
  }
}

void Task::push_back(std::function<void ()> f) {
  check_not_running();

  auto f_notify = [this, f = std::move(f)]() {
    f() ;
    {
      std::unique_lock<std::mutex> lock(m_running_mutex);
      m_numRunning--;
    }
    m_condVar.notify_all();
  };

  std::lock_guard<std::mutex> lock(m_functions_mutex);
  m_functions.push_back(std::make_shared<std::function<void()>>(std::move(f_notify)));
}

void Task::clear() {
  check_not_running();
  std::lock_guard<std::mutex> lock(m_functions_mutex);
  m_functions.clear();
}

void Task::enqueue_all(Threads &threads) {
  check_not_running();

  std::unique_lock<std::mutex> lock(m_functions_mutex);
  m_numRunning = m_functions.size();
  for(size_t i=0; i<m_functions.size(); i++) {
    threads.enqueue(m_functions.at(i), i % threads.getNumThreads());
  }
}

void Task::wait() {
    std::unique_lock<std::mutex> lock(m_running_mutex);
    while (m_numRunning > 0) {
        m_condVar.wait(lock);
    }

    if (m_numRunning > 0) {
      throw std::logic_error("Some functions are still running after wait.");
    }
}

}  // namespace threads
