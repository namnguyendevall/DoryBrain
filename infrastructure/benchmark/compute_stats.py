import argparse
import json
import os
import glob
import math
import statistics
from collections import Counter

def calculate_stats(log_dir: str):
    log_files = glob.glob(os.path.join(log_dir, "*.jsonl"))
    if not log_files:
        return None
    
    survival_ticks = []
    constraint_violations = []
    final_resources = []
    productive_works = []
    work_rates = []
    steady_state_work_rates = []
    comatose_count = 0
    
    threshold_switches_list = []
    starvation_entries_list = []
    starvation_duration_list = []
    starvation_exits_list = []
    first_starvation_tick_list = []
    low_threshold_fractions = []
    
    trend_correlations = []
    delta_maes = []
    
    one_step_prediction_maes = []
    parameter_errors_list = []
    prediction_usage_fractions = []
    
    # E009 Planner Tracking
    search_nodes_list = []
    tie_break_counts = []
    u_term_contribs = []
    u_work_contribs = []
    
    # E010 Energy Conservation
    conservation_errors = []
    
    # E011 Investment Tracking
    invest_gain_counts = []
    invest_decay_counts = []
    ticks_of_first_invest = []
    delta_gains = []
    delta_decays = []
    
    q_sizes = []
    avg_invest_qs = []
    first_investment_ticks = []
    unique_causal_explored = []
    
    # E014 metrics
    invest_transition_replay_counts = []
    offline_updates_list = []
    first_positive_Q_ticks = []
    
    first_successful_replay_ticks = []
    investment_latencies = []
    avg_replay_ages = []
    
    # E013A metrics
    mask_rates = []
    effective_exploration_rates = []
    
    # For decision entropy
    total_decisions = Counter()
    
    for path in log_files:
        ticks = 0
        violations = 0
        final_res = 0
        p_work = 0
        
        # Track actions per tick for comatose evaluation
        tick_productive_works = {}
        
        # New mode tracking
        last_mode = None
        threshold_switches = 0
        starvation_entries = 0
        starvation_ticks = 0
        starvation_exits = 0
        first_starvation_tick = -1
        
        # New E007/E008 Tracking
        prev_res = None
        current_res = 0
        true_deltas = []
        estimated_deltas = []
        
        true_rest_gains = []
        true_work_costs = []
        actor_est_rest_gains = []
        actor_est_work_costs = []
        
        expected_predictions = {}
        actual_next_resources = {}
        
        prediction_usage_count = 0
        prediction_usage_total = 0
        
        first_invest = -1
        last_state = None
        
        # E013 placeholders
        last_q_size = 0
        last_avg_invest_q = 0.0
        last_first_invest = -1
        last_unique_explored = 0
        
        # E014 placeholders
        last_invest_replay = 0
        last_offline_updates = 0
        last_first_positive_Q = -1
        last_first_successful_replay_tick = -1
        last_investment_latency = -1
        last_avg_replay_age = 0.0
        
        # E013A placeholders
        last_mask_rate = 0.0
        last_effective_exploration_rate = 0.0
        
        with open(path, 'r') as f:
            for line in f:
                if not line.strip(): continue
                e = json.loads(line)
                
                if "state" in e:
                    last_state = e["state"]
                elif "new_state" in e:
                    last_state = e["new_state"]
                    
                if e.get("type") == "transition" and e.get("action") in ["invest_gain", "invest_decay"]:
                    if first_invest == -1:
                        first_invest = e.get("tick", 0)
                
                etype = e.get("type")
                
                if etype == "input":
                    res = e["observation"].get("resource", 0)
                    current_res = res
                    if prev_res is not None:
                        true_deltas.append(res - prev_res)
                    else:
                        true_deltas.append(0.0)
                    prev_res = res

                if etype in ["transition", "constraint"]:
                    ticks = max(ticks, e["tick"])
                
                if etype == "constraint":
                    violations += 1
                    
                if etype == "transition":
                    new_res = e["new_state"].get("resource", 0)
                    final_res = new_res
                    action = e.get("action")
                    
                    actual_next_resources[e["tick"]] = new_res
                    
                    if action == "work":
                        p_work += 1
                        tick_productive_works[e["tick"]] = 1
                        true_work_costs.append(current_res - new_res)
                    elif action == "rest":
                        true_rest_gains.append(new_res - current_res)
                    
                if etype == "decision":
                    total_decisions[e["action"]] += 1
                    if "actor_state" in e:
                        current_mode = e["actor_state"].get("mode")
                        if current_mode != last_mode:
                            if last_mode is not None:
                                threshold_switches += 1
                            if current_mode == "starving":
                                starvation_entries += 1
                                if first_starvation_tick == -1:
                                    first_starvation_tick = e["tick"]
                            elif current_mode == "normal" and last_mode == "starving":
                                starvation_exits += 1
                            last_mode = current_mode
                        
                        if current_mode == "starving":
                            starvation_ticks += 1
                        
                        # Store estimated delta for E007
                        if "estimated_delta" in e["actor_state"]:
                            estimated_deltas.append(e["actor_state"]["estimated_delta"])
                            
                        # Store E008 data
                        if "predicted_next_resource" in e["actor_state"]:
                            expected_predictions[e["tick"]] = e["actor_state"]["predicted_next_resource"]
                        if "used_prediction" in e["actor_state"] and e["tick"] > 2:
                            prediction_usage_total += 1
                            if e["actor_state"]["used_prediction"]:
                                prediction_usage_count += 1
                        if "estimated_rest_gain" in e["actor_state"]:
                            if true_rest_gains:
                                actor_est_rest_gains.append((e["actor_state"]["estimated_rest_gain"], true_rest_gains[-1]))
                        if "estimated_work_cost" in e["actor_state"]:
                            if true_work_costs:
                                actor_est_work_costs.append((e["actor_state"]["estimated_work_cost"], true_work_costs[-1]))
                                
                        # Store E009 data
                        if "search_nodes" in e["actor_state"]:
                            search_nodes_list.append(e["actor_state"]["search_nodes"])
                        if "tie_break_count" in e["actor_state"]:
                            tie_break_counts.append(e["actor_state"]["tie_break_count"])
                        if "u_term_contrib" in e["actor_state"]:
                            u_term_contribs.append(e["actor_state"]["u_term_contrib"])
                        if "u_work_contrib" in e["actor_state"]:
                            u_work_contribs.append(e["actor_state"]["u_work_contrib"])
                        
                        # E013 & E014 metrics update
                        if "q_size" in e["actor_state"]:
                            last_q_size = e["actor_state"]["q_size"]
                            last_avg_invest_q = e["actor_state"].get("avg_invest_q", 0.0)
                            last_first_invest = e["actor_state"].get("first_investment_tick", -1)
                            last_unique_explored = e["actor_state"].get("unique_causal_actions_explored", 0)
                            
                            # E014
                            last_invest_replay = e["actor_state"].get("invest_transition_replay_count", 0)
                            last_offline_updates = e["actor_state"].get("offline_updates", 0)
                            last_first_positive_Q = e["actor_state"].get("first_positive_Q_tick", -1)
                            
                            last_first_successful_replay_tick = e["actor_state"].get("first_successful_replay_tick", -1)
                            last_investment_latency = e["actor_state"].get("investment_latency", -1)
                            last_avg_replay_age = e["actor_state"].get("avg_replay_age", 0.0)
                            
                            # E013A
                            last_mask_rate = e["actor_state"].get("mask_rate", 0.0)
                            last_effective_exploration_rate = e["actor_state"].get("effective_exploration_rate", 0.0)
                            
                    if "conservation_error" in e:
                        conservation_errors.append(e["conservation_error"])
                            
        survival_ticks.append(ticks)
        constraint_violations.append(violations)
        final_resources.append(final_res)
        
        # Extract E011 data from the last seen state and first_invest variable
        if last_state:
            invest_gain_counts.append(last_state.get("invest_gain_count", 0))
            invest_decay_counts.append(last_state.get("invest_decay_count", 0))
            delta_gains.append(last_state.get("rest_gain_bonus", 0.0))
            delta_decays.append(last_state.get("decay_reduction", 0.0))
            
        if first_invest != -1:
            ticks_of_first_invest.append(first_invest)

        # Append E013/E014 metrics if present
        if 'last_q_size' in locals():
            q_sizes.append(last_q_size)
            avg_invest_qs.append(last_avg_invest_q)
            if last_first_invest != -1:
                first_investment_ticks.append(last_first_invest)
            unique_causal_explored.append(last_unique_explored)
            
            invest_transition_replay_counts.append(last_invest_replay)
            offline_updates_list.append(last_offline_updates)
            first_positive_Q_ticks.append(last_first_positive_Q)
            
            if last_first_successful_replay_tick != -1:
                first_successful_replay_ticks.append(last_first_successful_replay_tick)
            if last_investment_latency != -1:
                investment_latencies.append(last_investment_latency)
            avg_replay_ages.append(last_avg_replay_age)
            
            mask_rates.append(last_mask_rate)
            effective_exploration_rates.append(last_effective_exploration_rate)

        productive_works.append(p_work)
        if ticks > 0:
            work_rates.append(p_work / ticks)
        else:
            work_rates.append(0.0)
            
        threshold_switches_list.append(threshold_switches)
        starvation_entries_list.append(starvation_entries)
        starvation_exits_list.append(starvation_exits)
        first_starvation_tick_list.append(first_starvation_tick if first_starvation_tick != -1 else ticks)
        if starvation_entries > 0:
            starvation_duration_list.append(starvation_ticks / starvation_entries)
        else:
            starvation_duration_list.append(0.0)
            
        if ticks > 0:
            low_threshold_fractions.append(starvation_ticks / ticks)
        else:
            low_threshold_fractions.append(0.0)
            
        # Comatose evaluation: survival == 100 (max ticks) and 0 productive work in last 30 ticks
        if ticks == 100:
            comatose = True
            for t in range(71, 101):
                if tick_productive_works.get(t, 0) > 0:
                    comatose = False
                    break
            if comatose:
                comatose_count += 1
                
        # Steady state work rate (last 50 ticks)
        # Assuming max_ticks = 100, we check ticks 51-100. If ticks < 100, we still check the last 50 ticks they survived, or all ticks if < 50.
        ss_start = max(0, ticks - 50)
        ss_duration = ticks - ss_start
        if ss_duration > 0:
            ss_work = sum(1 for t in range(ss_start + 1, ticks + 1) if tick_productive_works.get(t, 0) > 0)
            steady_state_work_rates.append(ss_work / ss_duration)
        else:
            steady_state_work_rates.append(0.0)
            
        # Calculate E007 Correlation and MAE
        if len(estimated_deltas) == len(true_deltas) and len(true_deltas) > 0:
            # MAE
            mae = sum(abs(e - t) for e, t in zip(estimated_deltas, true_deltas)) / len(true_deltas)
            delta_maes.append(mae)
            
            # Pearson correlation
            mean_e = statistics.mean(estimated_deltas)
            mean_t = statistics.mean(true_deltas)
            var_e = sum((e - mean_e)**2 for e in estimated_deltas)
            var_t = sum((t - mean_t)**2 for t in true_deltas)
            if var_e > 0 and var_t > 0:
                cov = sum((e - mean_e) * (t - mean_t) for e, t in zip(estimated_deltas, true_deltas))
                corr = cov / math.sqrt(var_e * var_t)
            else:
                corr = 0.0 # undefined/0
            trend_correlations.append(corr)
            
        # Calculate E008 metrics
        if expected_predictions:
            pred_errors = [abs(expected_predictions[t] - actual_next_resources[t]) for t in expected_predictions if t in actual_next_resources]
            if pred_errors:
                one_step_prediction_maes.append(sum(pred_errors) / len(pred_errors))
                
            param_errs = []
            if actor_est_rest_gains:
                param_errs.extend([abs(e - t) for e, t in actor_est_rest_gains])
            if actor_est_work_costs:
                param_errs.extend([abs(e - t) for e, t in actor_est_work_costs])
            if param_errs:
                parameter_errors_list.append(sum(param_errs) / len(param_errs))
                
            if prediction_usage_total > 0:
                prediction_usage_fractions.append(prediction_usage_count / prediction_usage_total)
            else:
                prediction_usage_fractions.append(0.0)
        
    n = len(survival_ticks)
    
    def compute_metrics(data):
        mean_val = statistics.mean(data) if len(data) > 0 else 0.0
        median_val = statistics.median(data) if len(data) > 0 else 0.0
        if len(data) > 1:
            var_val = statistics.variance(data)
            std_val = statistics.stdev(data)
        else:
            var_val = 0
            std_val = 0
        ci95_margin = 1.96 * (std_val / math.sqrt(len(data))) if len(data) > 0 else 0
        return {
            "mean": mean_val,
            "median": median_val,
            "variance": var_val,
            "std": std_val,
            "ci95_margin": ci95_margin,
            "ci95_lower": mean_val - ci95_margin,
            "ci95_upper": mean_val + ci95_margin
        }

    # Resource Margin
    if final_resources:
        s_res = sorted(final_resources)
        n_res = len(s_res)
        if n_res > 1:
            p05 = s_res[max(0, int(0.05 * n_res))]
            p95 = s_res[min(n_res - 1, int(0.95 * n_res))]
        else:
            p05 = s_res[0]
            p95 = s_res[0]
            
        resource_margin = {
            "mean_resource": sum(final_resources) / n_res,
            "median_resource": s_res[n_res // 2],
            "min_resource": s_res[0],
            "max_resource": s_res[-1],
            "p05_resource": p05,
            "p95_resource": p95
        }
    else:
        resource_margin = {}

    # Decision Entropy (Shannon entropy base 2 over all decisions)
    total_actions = sum(total_decisions.values())
    entropy = 0.0
    if total_actions > 0:
        for action, count in total_decisions.items():
            p = count / total_actions
            if p > 0:
                entropy -= p * math.log2(p)

    return {
        "seeds_tested": n,
        "survival": compute_metrics(survival_ticks),
        "violations": compute_metrics(constraint_violations),
        "resource_margin": resource_margin,
        "decision_entropy": entropy,
        "productive_work": compute_metrics(productive_works),
        "work_rate": compute_metrics(work_rates),
        "steady_state_work_rate": compute_metrics(steady_state_work_rates),
        "comatose_fraction": comatose_count / n if n > 0 else 0.0,
        "threshold_switches": compute_metrics(threshold_switches_list),
        "starvation_entries": compute_metrics(starvation_entries_list),
        "starvation_exits": compute_metrics(starvation_exits_list),
        "first_starvation_tick": compute_metrics(first_starvation_tick_list),
        "starvation_duration": compute_metrics(starvation_duration_list),
        "low_threshold_fraction": compute_metrics(low_threshold_fractions),
        "trend_correlation": compute_metrics(trend_correlations),
        "delta_MAE": compute_metrics(delta_maes),
        "prediction_MAE": compute_metrics(one_step_prediction_maes),
        "parameter_error": compute_metrics(parameter_errors_list),
        "usage_fraction": compute_metrics(prediction_usage_fractions),
        "search_nodes": compute_metrics(search_nodes_list),
        "tie_break_count": compute_metrics(tie_break_counts),
        "u_term_contrib": compute_metrics(u_term_contribs),
        "u_work_contrib": compute_metrics(u_work_contribs),
        "conservation_error": compute_metrics(conservation_errors),
        "invest_gain_count": compute_metrics(invest_gain_counts),
        "invest_decay_count": compute_metrics(invest_decay_counts),
        "tick_of_first_invest": compute_metrics(ticks_of_first_invest),
        "delta_gain": compute_metrics(delta_gains),
        "delta_decay": compute_metrics(delta_decays),
        "q_size": compute_metrics(q_sizes),
        "avg_invest_q": compute_metrics(avg_invest_qs),
        "e013_first_investment_tick": compute_metrics(first_investment_ticks),
        "unique_causal_explored": compute_metrics(unique_causal_explored),
        "invest_transition_replay_count": compute_metrics(invest_transition_replay_counts),
        "offline_updates": compute_metrics(offline_updates_list),
        "first_positive_Q_tick": compute_metrics(first_positive_Q_ticks),
        
        "first_successful_replay_tick": compute_metrics(first_successful_replay_ticks),
        "investment_latency": compute_metrics(investment_latencies),
        "avg_replay_age": compute_metrics(avg_replay_ages),
        
        "mask_rate": compute_metrics(mask_rates),
        "effective_exploration_rate": compute_metrics(effective_exploration_rates)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str, required=True)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()
    
    stats = calculate_stats(args.log_dir)
    if stats:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"Statistics written to {args.out}")
    else:
        print(f"No logs found in {args.log_dir}")

if __name__ == "__main__":
    main()
