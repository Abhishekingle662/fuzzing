import math
import re
import os
import subprocess
from typing import List, Tuple, Any, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.utils import restricted_mean_survival_time

def parse_time(name: str) -> float:
	return float(re.findall(",time:([0-9]+),", name)[0]) / 1000

def unzip_list(list_of_tuples: List[Tuple[Any, Any]]) \
	-> Tuple[List[Any], List[Any]]:
	return tuple([list(group) for group in zip(*list_of_tuples)])

def compute_mean(
	data: List[Optional[float]], trial_len: float = math.inf) -> float:
	if all(d is None for d in data):
		return math.inf

	df = pd.DataFrame(data)
	kmf = KaplanMeierFitter()
	kmf.fit(df.fillna(trial_len), df.notnull())

	# Compute the restricted mean survival time and 95% confidence interval
	return restricted_mean_survival_time(kmf, t=trial_len)

def compute_mean_plot(plots: List[List[Tuple[float, float]]]) \
	-> List[Tuple[float, float]]:
	xs = set()
	for plot in plots:
		for i in range(0, len(plot)):
			xs.add(plot[i][0])
			if i > 0:
				assert plot[i-1][0] <= plot[i][0] and plot[i-1][1] <= plot[i][1]
	xs = list(xs)
	xs.sort()
	ys = []
	for plot in plots:
		xp, fp = unzip_list(plot)
		ys.append(np.interp(xs, xp, fp))
	ys = np.array(ys)
	avg = np.average(ys, axis=0)
	ret = []
	assert len(xs) == len(avg)
	for i in range(0, len(xs)):
		ret.append((xs[i], avg[i]))
	return ret

def plot_figure( \
	plot1: List[Tuple[float, float]], plot2: List[Tuple[float, float]],
	label1: str, label2: str, output: str):
	xs1, ys1 = unzip_list(plot1)
	xs2, ys2 = unzip_list(plot2)
	plt.figure()
	plt.plot(xs1, ys1, label=label1)
	plt.plot(xs2, ys2, label=label2)
	plt.legend()
	plt.savefig(output, bbox_inches='tight', dpi=300)
	plt.close()

if __name__ == "__main__":
	# TODO: Replace these lists with your 10 throughput values.
	throughput_asan = [257.72, 280.76, 250.50, 255.16, 253.11, 245.48, 265.50, 266.40, 269.85, 274.71]
	throughput_normal = [283.22, 265.02, 267.90, 281.03, 261.35, 258.40, 269.67, 265.77, 284.00, 265.88]
	assert len(throughput_asan) == 10 and len(throughput_normal) == 10
	print("Mean throughput for ASAN binary:",
		compute_mean(throughput_asan))
	print("Mean throughput for normal binary:",
		compute_mean(throughput_normal))

	# TODO: Replace these lists with your 10 TTE values,
	# where `None` represents 'timeout'.
	tte_asan = [None, None, None, 31.527, None, 28.340, None, 17.466, 7.356, None]
	tte_normal = [None, None, None, None, None, None, None, None, None, None]
	assert len(tte_asan) == 10 and len(tte_normal) == 10
	print("TTE for ASAN binary:", compute_mean(tte_asan, 60))
	print("TTE for normal binary:", compute_mean(tte_normal, 60))

	# TODO: Replace each of the variable with a list of 10 lists,
	# each consisting of pairs of ascending (time, coverage).
	cov_asan = [
		[(0.0, 3), (0.057, 4), (5.69, 5)],
		[(0.0, 3), (0.088, 4), (10.984, 5), (50.175, 6)],
		[(0.0, 3), (0.069, 4), (4.38, 5), (23.181, 6)],
		[(0.0, 3), (0.034, 4), (10.58, 5), (13.214, 6)],
		[(0.0, 3), (0.029, 4), (22.283, 5), (28.62, 6)],
		[(0.0, 3), (0.062, 4), (2.192, 5), (4.515, 6)],
		[(0.0, 3), (0.056, 4), (2.39, 5), (22.343, 6)],
		[(0.0, 3), (0.029, 4), (6.426, 5), (14.237, 6)],
		[(0.0, 3), (0.071, 4), (1.396, 5), (2.356, 6)],
		[(0.0, 3), (0.023, 4), (0.33, 5)]
		]

	cov_normal = [
		[(0.0, 3), (0.064, 4), (4.671, 5), (7.287, 6), (37.581, 7)],
		[(0.0, 3), (0.051, 4), (8.804, 5), (54.47, 6)],
		[(0.0, 3), (0.034, 4), (5.026, 5), (45.055, 6)],
		[(0.0, 3), (0.03, 4), (19.74, 5), (22.081, 6), (33.762, 7)],
		[(0.0, 3), (0.075, 4), (4.395, 5), (8.048, 6), (12.506, 7)],
		[(0.0, 3), (0.123, 4), (1.58, 5)],
		[(0.0, 3), (0.027, 4), (12.265, 5), (14.218, 6)],
		[(0.0, 3), (0.059, 4), (1.172, 5), (17.314, 6), (55.037, 7)],
		[(0.0, 3), (0.092, 4), (4.647, 5), (5.842, 6), (11.945, 7)],
		[(0.0, 3), (0.086, 4), (21.877, 5)]
		]

	assert len(cov_asan) == 10 and len(cov_normal) == 10
	plot_figure(compute_mean_plot(cov_asan),
		compute_mean_plot(cov_normal), "ASAN", "normal", "out/cov1.png")
	

	# TODO: Replace these lists with your 10 TTE values,
	# where `None` represents 'timeout'.
	tte_aflpp =  [None, None, None, None, None, None, None, None, None, None]
	tte_custom = [25.536, 20.729, None, None, None, None, None, 41.633, None, None]
	assert len(tte_aflpp) == 10 and len(tte_custom) == 10
	print("TTE for AFL++ mutator:", compute_mean(tte_aflpp, 60))
	print("TTE for custom mutator:", compute_mean(tte_custom, 60))

	# TODO: Replace each of the variable with a list of 10 lists,
	# each consisting of pairs of ascending (time, coverage).
	cov_aflpp = [[(0.0, 2), (0.072, 3), (0.22, 4)],
				[(0.0, 2), (0.066, 3), (0.113, 4)],
				[(0.0, 2), (0.089, 3), (0.201, 4)],
				[(0.0, 2), (0.089, 3), (0.259, 4)],
				[(0.0, 2), (0.054, 3), (0.113, 4)],
				[(0.0, 2), (0.103, 3), (0.159, 4)],
				[(0.0, 2), (0.104, 3), (0.28, 4)],
				[(0.0, 2), (0.114, 3), (0.242, 4)],
				[(0.0, 2), (0.064, 3), (0.121, 4)],
				[(0.0, 2), (0.059, 3), (0.114, 4)]]
	

	cov_custom = 	[[(0.0, 2), (0.012, 3), (0.088, 4), (4.139, 5), (17.656, 6)],
					[(0.0, 2), (0.011, 3), (0.087, 4), (7.824, 5), (10.136, 6), (12.758, 7)],
					[(0.0, 2), (0.011, 3), (0.092, 4), (30.501, 5), (33.434, 6), (36.172, 7)],
					[(0.0, 2), (0.017, 3), (0.104, 4), (38.55, 5), (58.113, 6)],
					[(0.0, 2), (0.012, 3), (0.085, 4), (14.304, 5), (36.442, 6)],
					[(0.0, 2), (0.011, 3), (0.106, 4), (4.436, 5)],
					[(0.0, 2), (0.021, 3), (0.096, 4), (16.18, 5)],
					[(0.0, 2), (0.014, 3), (0.085, 4), (5.174, 5), (8.713, 6)],
					[(0.0, 2), (0.01, 3), (0.072, 4), (8.693, 5), (29.085, 6), (30.772, 7)],
					[(0.0, 2), (0.014, 3), (0.113, 4), (6.134, 5), (9.204, 6)]]
	
	assert len(cov_aflpp) == 10 and len(cov_custom) == 10
	plot_figure(compute_mean_plot(cov_aflpp),
		compute_mean_plot(cov_custom), "original", "custom", "out/cov2.png")