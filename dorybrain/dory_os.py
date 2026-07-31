import time
import os
import sys
import threading
from experiments.E019C_Cognitive import Actor as E019C_CognitiveActor
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

# Biến toàn cục để điều khiển luồng
running = True
command_queue = []

def input_listener():
    """Luồng chạy ngầm để lắng nghe lệnh từ người dùng mà không chặn Dory."""
    global running
    while running:
        try:
            # Chờ người dùng nhập lệnh
            cmd = input().strip().lower()
            if cmd:
                command_queue.append(cmd)
            if cmd in ["exit", "quit"]:
                running = False
                break
        except:
            running = False
            break

def dory_speak(state, action, reward):
    resource = state.get('resource', 0)
    bank = state.get('bank', 0)
    
    dialogue = f"[Dory - Năng lượng: {resource:.1f} | Kho: {bank:.1f}] -> "
    
    if resource < 20:
        dialogue += "Trạng thái khẩn cấp! Năng lượng cạn kiệt... "
        
    if action == "work":
        dialogue += "Đi LÀM để kiếm tài nguyên."
    elif action == "rest":
        dialogue += "NGHỈ NGƠI để phục hồi."
    elif action == "store":
        dialogue += "Dư dả, CẤT VÀO KHO."
    elif action == "retrieve":
        dialogue += "Đói quá, RÚT TỪ KHO ra dùng!"
    elif action.startswith("invest"):
        dialogue += "ĐẦU TƯ nâng cấp bản thân!"
    else:
        dialogue += f"Hành động: {action}."
        
    if reward > 0:
        dialogue += f" (Thành công! +{reward})"
    elif reward < 0:
        dialogue += f" (Thất bại/Phạt {reward})"
        
    return dialogue

def run_agent_os():
    global running
    
    print("="*60)
    print(" 🧠 DORY OS - CHẾ ĐỘ TỰ TRỊ (AUTONOMOUS AGENT)")
    print("="*60)
    print("Dory đang sống và hoạt động liên tục độc lập.")
    print("Bạn có thể gõ các lệnh sau BẤT CỨ LÚC NÀO (không cần đợi dấu nhắc):")
    print(" - shock : Gây sát thương (trừ 50% tài nguyên)")
    print(" - gift  : Tặng 50 tài nguyên")
    print(" - exit  : Tắt hệ thống")
    print("="*60)

    # Khởi tạo thế giới
    config = load_constraint_set("default-v1")
    system = SystemPhysics(config)
    
    # Khởi tạo Dory
    genome = CognitiveGenome()
    genome.beta = 64.0 
    dory = E019C_CognitiveActor(seed=42, genome=genome)
    
    state = system.get_initial_state()
    tick = 0
    work_reward = 10.0
    
    # Khởi động luồng lắng nghe lệnh
    listener = threading.Thread(target=input_listener, daemon=True)
    listener.start()
    
    while running:
        # Xử lý các lệnh người dùng vừa gõ (nếu có)
        while len(command_queue) > 0:
            cmd = command_queue.pop(0)
            if cmd == "shock":
                state["resource"] *= 0.5
                print(f"\n⚡ [SYSTEM INJECT] Bạn vừa giáng họa! Năng lượng Dory bị giảm một nửa!\n")
            elif cmd == "gift":
                state["resource"] += 50
                print(f"\n🎁 [SYSTEM INJECT] Bạn vừa ban phước! Dory nhận được 50 năng lượng!\n")
            elif cmd == "exit":
                print("Tắt Dory OS...")
                return

        # Dory hành động tự chủ
        tick += 1
        state = system.system_tick(state)
        
        if system.is_terminal(state):
            print("\n💀 Dory đã cạn kiệt năng lượng và gục ngã...")
            running = False
            break
            
        obs = system.system_observe(state, tick)
        decision = dory.choose(obs)
        is_valid, _ = system.system_validate(state, decision)
        
        if is_valid:
            state = system.system_apply(state, decision)
            
        reward = -1.0 if not is_valid else (work_reward if decision == "work" else 0.0)
        
        dory.update(str(obs), decision, reward, str(system.system_observe(state, tick)))
        
        # In suy nghĩ của Dory
        print(f"Tick {tick:04d} | " + dory_speak(state, decision, reward))
        
        # Ngủ 0.8 giây để con người kịp đọc tốc độ hoạt động của Agent
        time.sleep(0.8)

if __name__ == "__main__":
    run_agent_os()
    print("Hệ thống đã dừng hoàn toàn.")
