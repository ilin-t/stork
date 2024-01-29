class Runner:
    def __init__(self):
        self._jobs: List[Job] = list()

    @property
    def jobs(self) -> List[Job]:
        return self._jobs

    def register(
        self,
        problem: Problem,
        client_config: ClientConfig,
        num_samples: int = 1,
        label: str = "",
    ):
        job_list: List[Job] = [Job(str(uuid4()), problem, client_config, label) for _ in range(num_samples)]
        self._jobs.extend(job_list)

    def run(self) -> BenchmarkResult:
        results: List[JobResult] = list()
        try:

            def handler(signum, frame) -> None:
                raise OSError(f"signal.SIGTERM. PID={os.getpid()}")

            signal.signal(signal.SIGTERM, handler)
            for job in self._jobs:
                results.append(_run_job_impl(job))
        except Exception as err:
            print(f"{type(err).__name__}: {err}")
        finally:
            self._jobs.clear()
            return BenchmarkResult(results)