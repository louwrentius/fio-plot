import bench_fio
import sys

if __name__ == '__main__':
    try:
        bench_fio.main()
    except KeyboardInterrupt:
        print("\nControl-C pressed - quitting...")
        sys.exit(1)
