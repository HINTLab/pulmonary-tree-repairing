import concurrent.futures
import multiprocessing
import time
from tqdm import tqdm
import warnings

AVAILABLE_CORES = multiprocessing.cpu_count()

print('Cores available:', AVAILABLE_CORES)

class TaskRunner:
    def __init__(self, task, arg_list, max_workers=AVAILABLE_CORES // 2, use_tqdm=True):
        self.max_workers = max_workers
        self.task = task
        self.arg_list = arg_list
        self.use_tqdm = use_tqdm

    def run(self, *args, **kwargs):
        self.now = time.time()
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._task, arg, *args, **kwargs) for arg in self.arg_list}
            completed = concurrent.futures.as_completed(futures)
            if self.use_tqdm:
                completed = tqdm(completed, total=len(self.arg_list))
            self.results_ = [future.result() for future in completed]
        print("Finished all @%ss" % (time.time() - self.now))

    def _task(self, arg, *args, **kwargs):
        try:
            ret = self.task(arg, *args, **kwargs)
        except Exception as e:
            warnings.warn("TASK ERROR:=====" + str(e) + "=====" + str(arg))
            return "error", arg, None
        if not self.use_tqdm:
            print("Finished %s @%ss" % (arg, time.time() - self.now))
        return "success", arg, ret

    @property
    def errors_(self):
        if not hasattr(self, "results_"):
            raise AttributeError
        return [r[1] for r in self.results_ if r[0] == "error"]

def example_task(arg, train_dir, group):
    time.sleep(1)
    return f"Processed {arg} with {train_dir} in {group}"

if __name__ == '__main__':
    arg_list = [1, 2, 3, 4, 5]
    runner = TaskRunner(example_task, arg_list,max_workers=5)
    runner.run("some_train_dir", "some_group")
    print("Results:", runner.results_)
    print("Errors:", runner.errors_)
