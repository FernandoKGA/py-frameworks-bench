---
layout: home
list_title: Archive
description: Python frameworks benchmarks
---

<script src="https://cdn.jsdelivr.net/npm/chart.js@3.2.1/dist/chart.min.js"></script>

This is a simple benchmark for python async frameworks. Almost all of the
frameworks are ASGI-compatible (aiohttp and tornado are exceptions on the
moment).

The objective of the benchmark is not testing deployment (like uvicorn vs
hypercorn and etc) or database (ORM, drivers) but instead test the frameworks
itself. The benchmark checks request parsing (body, headers, formdata,
queries), routing, responses.

* Read about the benchmark: [The Methodic](methodic.md)
* Check complete results for the latest benchmark here: [Results (2025-09-28)](_posts/2025-09-28-results.md)

[![benchmarks](https://github.com/klen/py-frameworks-bench/actions/workflows/benchmarks.yml/badge.svg)](https://github.com/klen/py-frameworks-bench/actions/workflows/benchmarks.yml)
[![tests](https://github.com/klen/py-frameworks-bench/actions/workflows/tests.yml/badge.svg)](https://github.com/klen/py-frameworks-bench/actions/workflows/tests.yml)

## Combined results

<canvas id="chart" style="margin-bottom: 2em"></canvas>
<script>
    var ctx = document.getElementById('chart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['fastapi.0.100.0','fastapi.0.100.1','fastapi.0.101.0','fastapi.0.101.1','fastapi.0.102.0','fastapi.0.103.0','fastapi.0.103.1','fastapi.0.103.2','fastapi.0.104.0','fastapi.0.104.1','fastapi.0.105.0','fastapi.0.106.0','fastapi.0.107.0','fastapi.0.108.0','fastapi.0.109.0','fastapi.0.109.1','fastapi.0.109.2','fastapi.0.110.0','fastapi.0.110.1','fastapi.0.110.2','fastapi.0.110.3','fastapi.0.110.3.dev1','fastapi.0.110.3.dev2','fastapi.0.111.0','fastapi.0.111.0.dev1','fastapi.0.111.1','fastapi.0.112.0','fastapi.0.112.1','fastapi.0.112.2','fastapi.0.112.3','fastapi.0.112.4','fastapi.0.113.0','fastapi.0.114.0','fastapi.0.114.1','fastapi.0.114.2','fastapi.0.115.0','fastapi.0.115.1','fastapi.0.115.10','fastapi.0.115.11','fastapi.0.115.12','fastapi.0.115.13','fastapi.0.115.14','fastapi.0.115.2','fastapi.0.115.3','fastapi.0.115.4','fastapi.0.115.5','fastapi.0.115.6','fastapi.0.115.7','fastapi.0.115.8','fastapi.0.115.9','fastapi.0.116.0','fastapi.0.116.1','fastapi.0.116.2','fastapi.0.117.0','fastapi.0.117.1','fastapi.0.51.0','fastapi.0.52.0','fastapi.0.53.0','fastapi.0.53.1','fastapi.0.53.2','fastapi.0.54.0','fastapi.0.54.1','fastapi.0.54.2','fastapi.0.55.0','fastapi.0.55.1','fastapi.0.56.0','fastapi.0.56.1','fastapi.0.57.0','fastapi.0.58.0','fastapi.0.58.1','fastapi.0.59.0','fastapi.0.60.0','fastapi.0.60.1','fastapi.0.60.2','fastapi.0.61.0','fastapi.0.61.1','fastapi.0.61.2','fastapi.0.62.0','fastapi.0.63.0','fastapi.0.64.0','fastapi.0.65.0','fastapi.0.65.1','fastapi.0.65.2','fastapi.0.65.3','fastapi.0.66.0','fastapi.0.66.1','fastapi.0.67.0','fastapi.0.68.0','fastapi.0.68.1','fastapi.0.68.2','fastapi.0.69.0','fastapi.0.70.0','fastapi.0.70.1','fastapi.0.71.0','fastapi.0.72.0','fastapi.0.73.0','fastapi.0.74.0','fastapi.0.74.1','fastapi.0.75.0','fastapi.0.75.1','fastapi.0.75.2','fastapi.0.76.0','fastapi.0.77.0','fastapi.0.77.1','fastapi.0.78.0','fastapi.0.79.0','fastapi.0.79.1','fastapi.0.80.0','fastapi.0.81.0','fastapi.0.82.0','fastapi.0.83.0','fastapi.0.84.0','fastapi.0.85.0','fastapi.0.85.1','fastapi.0.85.2','fastapi.0.86.0','fastapi.0.87.0','fastapi.0.88.0','fastapi.0.89.0','fastapi.0.89.1','fastapi.0.90.0','fastapi.0.90.1','fastapi.0.91.0','fastapi.0.92.0','fastapi.0.93.0','fastapi.0.94.0','fastapi.0.94.1','fastapi.0.95.0','fastapi.0.95.1','fastapi.0.95.2','fastapi.0.96.0','fastapi.0.96.1','fastapi.0.97.0','fastapi.0.98.0','fastapi.0.99.0','fastapi.0.99.1',],
            datasets: [
                {
                    label: '# of requests',
                    data: ['947430','927165','942660','936615','946620','949530','942435','939735','954210','948525','941790','941025','901260','877110','756945','774525','770835','768870','763905','766260','754215','773130','764655','764265','762435','762105','747570','766515','763755','760725','751215','744315','750510','757920','750315','731400','726195','834345','842295','846975','849390','853740','838515','835815','851940','841515','846090','847650','852225','833550','847350','843150','837990','849900','844620','1011570','1011150','1022565','992940','1000905','1009890','1017255','1010130','1014015','1017315','1012245','1014165','1008360','1010595','1018200','1018365','1016865','1025715','1041465','1041690','1036245','1050780','1063335','1063635','1041030','1066905','1049145','1059765','1058250','1053345','1050765','1055475','1047795','1065855','1058235','1062195','1037250','1066485','1045500','1048680','1050030','1067700','1005990','1023465','1023405','1038195','975120','998160','992430','972600','972645','969420','975675','978195','971430','978045','976740','980100','964935','964695','963045','964095','964080','981825','959625','966435','965385','975285','976470','961380','966510','965070','976485','967260','976860','960930','973845','979965','964545','978105','961575',],
                    backgroundColor: [
                        '#4E79A7', '#A0CBE8', '#F28E2B', '#FFBE7D', '#59A14F', '#8CD17D', '#B6992D', '#F1CE63', '#499894', '#86BCB6', '#E15759', '#FF9D9A', '#79706E', '#BAB0AC', '#D37295', '#FABFD2', '#B07AA1', '#D4A6C8', '#9D7660', '#D7B5A6',
                    ]
                },
            ]
        }
    });
</script>

Sorted by sum of completed requests

| Framework | Requests completed | Avg Latency 50% (ms) | Avg Latency 75% (ms) | Avg Latency (ms) |
| --------- | -----------------: | -------------------: | -------------------: | ---------------: |
| [fastapi.0.100.0](https://pypi.org/project/fastapi.0.100.0/) `` | 947430 | 8.29 | 8.64 | 9.74
| [fastapi.0.100.1](https://pypi.org/project/fastapi.0.100.1/) `` | 927165 | 8.35 | 8.78 | 9.99
| [fastapi.0.101.0](https://pypi.org/project/fastapi.0.101.0/) `` | 942660 | 8.29 | 8.79 | 9.69
| [fastapi.0.101.1](https://pypi.org/project/fastapi.0.101.1/) `` | 936615 | 8.3 | 8.72 | 10.12
| [fastapi.0.102.0](https://pypi.org/project/fastapi.0.102.0/) `` | 946620 | 8.31 | 8.7 | 9.57
| [fastapi.0.103.0](https://pypi.org/project/fastapi.0.103.0/) `` | 949530 | 8.26 | 8.66 | 9.45
| [fastapi.0.103.1](https://pypi.org/project/fastapi.0.103.1/) `` | 942435 | 8.25 | 8.66 | 9.78
| [fastapi.0.103.2](https://pypi.org/project/fastapi.0.103.2/) `` | 939735 | 8.29 | 8.7 | 9.56
| [fastapi.0.104.0](https://pypi.org/project/fastapi.0.104.0/) `` | 954210 | 8.27 | 8.66 | 9.5
| [fastapi.0.104.1](https://pypi.org/project/fastapi.0.104.1/) `` | 948525 | 8.24 | 8.6 | 9.45
| [fastapi.0.105.0](https://pypi.org/project/fastapi.0.105.0/) `` | 941790 | 8.24 | 8.61 | 10.04
| [fastapi.0.106.0](https://pypi.org/project/fastapi.0.106.0/) `` | 941025 | 8.31 | 8.77 | 9.96
| [fastapi.0.107.0](https://pypi.org/project/fastapi.0.107.0/) `` | 901260 | 8.54 | 8.9 | 10.35
| [fastapi.0.108.0](https://pypi.org/project/fastapi.0.108.0/) `` | 877110 | 8.54 | 9.05 | 15.18
| [fastapi.0.109.0](https://pypi.org/project/fastapi.0.109.0/) `` | 756945 | 9.24 | 9.68 | 23.43
| [fastapi.0.109.1](https://pypi.org/project/fastapi.0.109.1/) `` | 774525 | 9.3 | 9.75 | 11.12
| [fastapi.0.109.2](https://pypi.org/project/fastapi.0.109.2/) `` | 770835 | 9.21 | 9.69 | 10.94
| [fastapi.0.110.0](https://pypi.org/project/fastapi.0.110.0/) `` | 768870 | 9.25 | 9.67 | 11.01
| [fastapi.0.110.1](https://pypi.org/project/fastapi.0.110.1/) `` | 763905 | 9.32 | 9.8 | 11.27
| [fastapi.0.110.2](https://pypi.org/project/fastapi.0.110.2/) `` | 766260 | 9.26 | 9.76 | 11.0
| [fastapi.0.110.3](https://pypi.org/project/fastapi.0.110.3/) `` | 754215 | 9.28 | 9.8 | 22.29
| [fastapi.0.110.3.dev1](https://pypi.org/project/fastapi.0.110.3.dev1/) `` | 773130 | 9.23 | 9.63 | 11.0
| [fastapi.0.110.3.dev2](https://pypi.org/project/fastapi.0.110.3.dev2/) `` | 764655 | 9.36 | 9.76 | 11.35
| [fastapi.0.111.0](https://pypi.org/project/fastapi.0.111.0/) `` | 764265 | 9.32 | 9.75 | 11.05
| [fastapi.0.111.0.dev1](https://pypi.org/project/fastapi.0.111.0.dev1/) `` | 762435 | 9.33 | 9.81 | 11.41
| [fastapi.0.111.1](https://pypi.org/project/fastapi.0.111.1/) `` | 762105 | 9.27 | 9.63 | 11.13
| [fastapi.0.112.0](https://pypi.org/project/fastapi.0.112.0/) `` | 747570 | 9.28 | 9.78 | 23.05
| [fastapi.0.112.1](https://pypi.org/project/fastapi.0.112.1/) `` | 766515 | 9.28 | 9.65 | 10.93
| [fastapi.0.112.2](https://pypi.org/project/fastapi.0.112.2/) `` | 763755 | 9.25 | 9.71 | 11.17
| [fastapi.0.112.3](https://pypi.org/project/fastapi.0.112.3/) `` | 760725 | 9.25 | 9.82 | 11.0
| [fastapi.0.112.4](https://pypi.org/project/fastapi.0.112.4/) `` | 751215 | 9.4 | 9.83 | 11.36
| [fastapi.0.113.0](https://pypi.org/project/fastapi.0.113.0/) `` | 744315 | 9.45 | 9.83 | 10.97
| [fastapi.0.114.0](https://pypi.org/project/fastapi.0.114.0/) `` | 750510 | 9.41 | 9.8 | 11.27
| [fastapi.0.114.1](https://pypi.org/project/fastapi.0.114.1/) `` | 757920 | 9.28 | 9.72 | 11.18
| [fastapi.0.114.2](https://pypi.org/project/fastapi.0.114.2/) `` | 750315 | 9.37 | 9.85 | 11.34
| [fastapi.0.115.0](https://pypi.org/project/fastapi.0.115.0/) `` | 731400 | 9.59 | 9.97 | 11.37
| [fastapi.0.115.1](https://pypi.org/project/fastapi.0.115.1/) `` | 726195 | 9.61 | 10.1 | 11.21
| [fastapi.0.115.10](https://pypi.org/project/fastapi.0.115.10/) `` | 834345 | 8.78 | 9.19 | 10.66
| [fastapi.0.115.11](https://pypi.org/project/fastapi.0.115.11/) `` | 842295 | 8.81 | 9.21 | 10.11
| [fastapi.0.115.12](https://pypi.org/project/fastapi.0.115.12/) `` | 846975 | 8.72 | 9.07 | 10.44
| [fastapi.0.115.13](https://pypi.org/project/fastapi.0.115.13/) `` | 849390 | 8.63 | 9.08 | 10.29
| [fastapi.0.115.14](https://pypi.org/project/fastapi.0.115.14/) `` | 853740 | 8.72 | 9.04 | 10.23
| [fastapi.0.115.2](https://pypi.org/project/fastapi.0.115.2/) `` | 838515 | 8.73 | 9.21 | 10.45
| [fastapi.0.115.3](https://pypi.org/project/fastapi.0.115.3/) `` | 835815 | 8.73 | 9.24 | 10.45
| [fastapi.0.115.4](https://pypi.org/project/fastapi.0.115.4/) `` | 851940 | 8.69 | 9.08 | 9.98
| [fastapi.0.115.5](https://pypi.org/project/fastapi.0.115.5/) `` | 841515 | 8.82 | 9.2 | 10.39
| [fastapi.0.115.6](https://pypi.org/project/fastapi.0.115.6/) `` | 846090 | 8.7 | 9.17 | 10.54
| [fastapi.0.115.7](https://pypi.org/project/fastapi.0.115.7/) `` | 847650 | 8.77 | 9.12 | 10.02
| [fastapi.0.115.8](https://pypi.org/project/fastapi.0.115.8/) `` | 852225 | 8.67 | 8.98 | 10.28
| [fastapi.0.115.9](https://pypi.org/project/fastapi.0.115.9/) `` | 833550 | 8.82 | 9.17 | 10.35
| [fastapi.0.116.0](https://pypi.org/project/fastapi.0.116.0/) `` | 847350 | 8.71 | 9.09 | 10.01
| [fastapi.0.116.1](https://pypi.org/project/fastapi.0.116.1/) `` | 843150 | 8.77 | 9.14 | 10.07
| [fastapi.0.116.2](https://pypi.org/project/fastapi.0.116.2/) `` | 837990 | 8.77 | 9.11 | 10.04
| [fastapi.0.117.0](https://pypi.org/project/fastapi.0.117.0/) `` | 849900 | 8.75 | 9.16 | 10.21
| [fastapi.0.117.1](https://pypi.org/project/fastapi.0.117.1/) `` | 844620 | 8.67 | 9.07 | 10.06
| [fastapi.0.51.0](https://pypi.org/project/fastapi.0.51.0/) `` | 1011570 | 9.99 | 10.71 | 10.65
| [fastapi.0.52.0](https://pypi.org/project/fastapi.0.52.0/) `` | 1011150 | 9.95 | 10.66 | 10.53
| [fastapi.0.53.0](https://pypi.org/project/fastapi.0.53.0/) `` | 1022565 | 9.82 | 10.55 | 10.41
| [fastapi.0.53.1](https://pypi.org/project/fastapi.0.53.1/) `` | 992940 | 10.05 | 10.71 | 10.62
| [fastapi.0.53.2](https://pypi.org/project/fastapi.0.53.2/) `` | 1000905 | 10.02 | 10.74 | 10.61
| [fastapi.0.54.0](https://pypi.org/project/fastapi.0.54.0/) `` | 1009890 | 9.88 | 10.65 | 10.46
| [fastapi.0.54.1](https://pypi.org/project/fastapi.0.54.1/) `` | 1017255 | 9.82 | 10.51 | 10.66
| [fastapi.0.54.2](https://pypi.org/project/fastapi.0.54.2/) `` | 1010130 | 9.87 | 10.63 | 10.45
| [fastapi.0.55.0](https://pypi.org/project/fastapi.0.55.0/) `` | 1014015 | 9.94 | 10.67 | 10.5
| [fastapi.0.55.1](https://pypi.org/project/fastapi.0.55.1/) `` | 1017315 | 9.8 | 10.5 | 10.39
| [fastapi.0.56.0](https://pypi.org/project/fastapi.0.56.0/) `` | 1012245 | 9.94 | 10.67 | 10.52
| [fastapi.0.56.1](https://pypi.org/project/fastapi.0.56.1/) `` | 1014165 | 9.86 | 10.6 | 10.61
| [fastapi.0.57.0](https://pypi.org/project/fastapi.0.57.0/) `` | 1008360 | 9.91 | 10.69 | 11.02
| [fastapi.0.58.0](https://pypi.org/project/fastapi.0.58.0/) `` | 1010595 | 9.9 | 10.62 | 10.51
| [fastapi.0.58.1](https://pypi.org/project/fastapi.0.58.1/) `` | 1018200 | 9.82 | 10.5 | 10.41
| [fastapi.0.59.0](https://pypi.org/project/fastapi.0.59.0/) `` | 1018365 | 9.9 | 10.62 | 10.49
| [fastapi.0.60.0](https://pypi.org/project/fastapi.0.60.0/) `` | 1016865 | 9.84 | 10.57 | 10.42
| [fastapi.0.60.1](https://pypi.org/project/fastapi.0.60.1/) `` | 1025715 | 7.7 | 8.07 | 8.79
| [fastapi.0.60.2](https://pypi.org/project/fastapi.0.60.2/) `` | 1041465 | 7.6 | 7.97 | 9.64
| [fastapi.0.61.0](https://pypi.org/project/fastapi.0.61.0/) `` | 1041690 | 7.67 | 8.01 | 8.7
| [fastapi.0.61.1](https://pypi.org/project/fastapi.0.61.1/) `` | 1036245 | 7.61 | 7.99 | 9.19
| [fastapi.0.61.2](https://pypi.org/project/fastapi.0.61.2/) `` | 1050780 | 7.59 | 7.91 | 8.62
| [fastapi.0.62.0](https://pypi.org/project/fastapi.0.62.0/) `` | 1063335 | 7.53 | 7.83 | 8.71
| [fastapi.0.63.0](https://pypi.org/project/fastapi.0.63.0/) `` | 1063635 | 7.56 | 7.87 | 8.55
| [fastapi.0.64.0](https://pypi.org/project/fastapi.0.64.0/) `` | 1041030 | 7.63 | 7.95 | 8.62
| [fastapi.0.65.0](https://pypi.org/project/fastapi.0.65.0/) `` | 1066905 | 7.54 | 7.83 | 8.52
| [fastapi.0.65.1](https://pypi.org/project/fastapi.0.65.1/) `` | 1049145 | 7.59 | 7.85 | 9.17
| [fastapi.0.65.2](https://pypi.org/project/fastapi.0.65.2/) `` | 1059765 | 7.49 | 7.73 | 8.47
| [fastapi.0.65.3](https://pypi.org/project/fastapi.0.65.3/) `` | 1058250 | 7.53 | 7.83 | 8.53
| [fastapi.0.66.0](https://pypi.org/project/fastapi.0.66.0/) `` | 1053345 | 7.61 | 7.87 | 8.6
| [fastapi.0.66.1](https://pypi.org/project/fastapi.0.66.1/) `` | 1050765 | 7.53 | 7.79 | 8.55
| [fastapi.0.67.0](https://pypi.org/project/fastapi.0.67.0/) `` | 1055475 | 7.53 | 7.83 | 8.52
| [fastapi.0.68.0](https://pypi.org/project/fastapi.0.68.0/) `` | 1047795 | 7.55 | 7.9 | 8.58
| [fastapi.0.68.1](https://pypi.org/project/fastapi.0.68.1/) `` | 1065855 | 7.47 | 7.7 | 8.46
| [fastapi.0.68.2](https://pypi.org/project/fastapi.0.68.2/) `` | 1058235 | 7.55 | 7.77 | 8.53
| [fastapi.0.69.0](https://pypi.org/project/fastapi.0.69.0/) `` | 1062195 | 7.48 | 7.75 | 8.5
| [fastapi.0.70.0](https://pypi.org/project/fastapi.0.70.0/) `` | 1037250 | 7.69 | 7.97 | 8.66
| [fastapi.0.70.1](https://pypi.org/project/fastapi.0.70.1/) `` | 1066485 | 7.5 | 7.74 | 8.48
| [fastapi.0.71.0](https://pypi.org/project/fastapi.0.71.0/) `` | 1045500 | 7.56 | 7.88 | 8.56
| [fastapi.0.72.0](https://pypi.org/project/fastapi.0.72.0/) `` | 1048680 | 7.52 | 7.81 | 8.49
| [fastapi.0.73.0](https://pypi.org/project/fastapi.0.73.0/) `` | 1050030 | 7.47 | 7.74 | 8.97
| [fastapi.0.74.0](https://pypi.org/project/fastapi.0.74.0/) `` | 1067700 | 7.41 | 7.66 | 8.4
| [fastapi.0.74.1](https://pypi.org/project/fastapi.0.74.1/) `` | 1005990 | 7.75 | 8.07 | 8.78
| [fastapi.0.75.0](https://pypi.org/project/fastapi.0.75.0/) `` | 1023465 | 7.6 | 7.84 | 8.59
| [fastapi.0.75.1](https://pypi.org/project/fastapi.0.75.1/) `` | 1023405 | 7.69 | 7.98 | 8.68
| [fastapi.0.75.2](https://pypi.org/project/fastapi.0.75.2/) `` | 1038195 | 7.57 | 7.79 | 8.57
| [fastapi.0.76.0](https://pypi.org/project/fastapi.0.76.0/) `` | 975120 | 7.89 | 8.16 | 8.91
| [fastapi.0.77.0](https://pypi.org/project/fastapi.0.77.0/) `` | 998160 | 7.73 | 8.0 | 8.73
| [fastapi.0.77.1](https://pypi.org/project/fastapi.0.77.1/) `` | 992430 | 7.73 | 7.97 | 8.74
| [fastapi.0.78.0](https://pypi.org/project/fastapi.0.78.0/) `` | 972600 | 7.85 | 8.14 | 8.87
| [fastapi.0.79.0](https://pypi.org/project/fastapi.0.79.0/) `` | 972645 | 7.77 | 8.22 | 8.9
| [fastapi.0.79.1](https://pypi.org/project/fastapi.0.79.1/) `` | 969420 | 7.85 | 8.28 | 8.94
| [fastapi.0.80.0](https://pypi.org/project/fastapi.0.80.0/) `` | 975675 | 7.82 | 8.12 | 8.87
| [fastapi.0.81.0](https://pypi.org/project/fastapi.0.81.0/) `` | 978195 | 7.78 | 8.18 | 8.86
| [fastapi.0.82.0](https://pypi.org/project/fastapi.0.82.0/) `` | 971430 | 7.79 | 8.19 | 8.86
| [fastapi.0.83.0](https://pypi.org/project/fastapi.0.83.0/) `` | 978045 | 7.7 | 8.12 | 8.78
| [fastapi.0.84.0](https://pypi.org/project/fastapi.0.84.0/) `` | 976740 | 7.73 | 8.07 | 8.81
| [fastapi.0.85.0](https://pypi.org/project/fastapi.0.85.0/) `` | 980100 | 7.85 | 8.25 | 8.93
| [fastapi.0.85.1](https://pypi.org/project/fastapi.0.85.1/) `` | 964935 | 7.84 | 8.17 | 9.57
| [fastapi.0.85.2](https://pypi.org/project/fastapi.0.85.2/) `` | 964695 | 7.87 | 8.27 | 8.94
| [fastapi.0.86.0](https://pypi.org/project/fastapi.0.86.0/) `` | 963045 | 7.82 | 8.22 | 9.84
| [fastapi.0.87.0](https://pypi.org/project/fastapi.0.87.0/) `` | 964095 | 8.15 | 8.52 | 9.23
| [fastapi.0.88.0](https://pypi.org/project/fastapi.0.88.0/) `` | 964080 | 8.17 | 8.53 | 9.29
| [fastapi.0.89.0](https://pypi.org/project/fastapi.0.89.0/) `` | 981825 | 8.06 | 8.41 | 9.18
| [fastapi.0.89.1](https://pypi.org/project/fastapi.0.89.1/) `` | 959625 | 8.22 | 8.6 | 9.3
| [fastapi.0.90.0](https://pypi.org/project/fastapi.0.90.0/) `` | 966435 | 8.07 | 8.42 | 9.21
| [fastapi.0.90.1](https://pypi.org/project/fastapi.0.90.1/) `` | 965385 | 8.12 | 8.53 | 9.25
| [fastapi.0.91.0](https://pypi.org/project/fastapi.0.91.0/) `` | 975285 | 7.91 | 8.32 | 9.01
| [fastapi.0.92.0](https://pypi.org/project/fastapi.0.92.0/) `` | 976470 | 7.8 | 8.17 | 8.83
| [fastapi.0.93.0](https://pypi.org/project/fastapi.0.93.0/) `` | 961380 | 7.81 | 8.18 | 8.92
| [fastapi.0.94.0](https://pypi.org/project/fastapi.0.94.0/) `` | 966510 | 7.84 | 8.25 | 8.92
| [fastapi.0.94.1](https://pypi.org/project/fastapi.0.94.1/) `` | 965070 | 7.86 | 8.26 | 8.93
| [fastapi.0.95.0](https://pypi.org/project/fastapi.0.95.0/) `` | 976485 | 7.74 | 8.13 | 8.81
| [fastapi.0.95.1](https://pypi.org/project/fastapi.0.95.1/) `` | 967260 | 7.86 | 8.22 | 8.92
| [fastapi.0.95.2](https://pypi.org/project/fastapi.0.95.2/) `` | 976860 | 7.7 | 8.07 | 8.78
| [fastapi.0.96.0](https://pypi.org/project/fastapi.0.96.0/) `` | 960930 | 7.8 | 8.14 | 8.85
| [fastapi.0.96.1](https://pypi.org/project/fastapi.0.96.1/) `` | 973845 | 7.74 | 8.17 | 9.58
| [fastapi.0.97.0](https://pypi.org/project/fastapi.0.97.0/) `` | 979965 | 7.67 | 8.05 | 8.73
| [fastapi.0.98.0](https://pypi.org/project/fastapi.0.98.0/) `` | 964545 | 7.83 | 8.26 | 8.91
| [fastapi.0.99.0](https://pypi.org/project/fastapi.0.99.0/) `` | 978105 | 7.69 | 8.11 | 8.76
| [fastapi.0.99.1](https://pypi.org/project/fastapi.0.99.1/) `` | 961575 | 7.69 | 8.18 | 9.94


More details: [Results (2025-09-28)](_posts/2025-09-28-results.md)