import random
import csv
import os


# Số lượng request cần sinh
DATA_SIZES = [
    1000,
    5000,
    10000,
    50000,
    100000
]


def generate_requests(n):
    requests = []

    for i in range(1, n + 1):

        request = {
            "request_id": f"REQ{i:06d}",
            "user_id": f"USER{random.randint(1, n):06d}",
            "timestamp": random.randint(1, 86400),
            "priority": random.randint(1, 10)
        }

        requests.append(request)

    return requests


def save_to_csv(requests, filename):

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "request_id",
            "user_id",
            "timestamp",
            "priority"
        ])

        for request in requests:

            writer.writerow([
                request["request_id"],
                request["user_id"],
                request["timestamp"],
                request["priority"]
            ])


def main():

    # Tạo thư mục data
    os.makedirs("data", exist_ok=True)

    for n in DATA_SIZES:

        print(f"Dang sinh {n:,} request...")

        requests = generate_requests(n)

        filename = f"data/requests_{n}.csv"

        save_to_csv(requests, filename)

        print(f"Da luu: {filename}")


if __name__ == "__main__":
    main()