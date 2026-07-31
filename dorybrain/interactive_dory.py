import time
import os
import sys
from experiments.E019C_Cognitive import Actor as E019C_CognitiveActor
from infrastructure.runner.loader import load_constraint_set
from infrastructure.runner.system import SystemPhysics
from infrastructure.evolution.genome import CognitiveGenome

def dory_speak(state, action, reward):
    """Chuyển đổi trạng thái và hành động của Dory thành lời thoại."""
    resource = state.get('resource', 0)
    bank = state.get('bank', 0)
    
    dialogue = f"[Dory - Năng lượng: {resource:.1f} | Kho: {bank:.1f}] -> "
    
    if resource < 20:
        dialogue += "Trạng thái khẩn cấp! Năng lượng của tôi đang cạn kiệt... "
        
    if action == "work":
        dialogue += "Tôi quyết định ĐI LÀM để kiếm tài nguyên."
    elif action == "rest":
        dialogue += "Tôi đang NGHỈ NGƠI để phục hồi năng lượng tự nhiên."
    elif action == "store":
        dialogue += "Tài nguyên dư dả, tôi đang CẤT VÀO KHO dự phòng."
    elif action == "retrieve":
        dialogue += "Đói quá, tôi phải RÚT TỪ KHO ra để sống sót!"
    elif action.startswith("invest"):
        dialogue += "Tôi đang ĐẦU TƯ để nâng cấp bản thân dài hạn!"
    else:
        dialogue += f"Tôi thử làm: {action}."
        
    if reward > 0:
        dialogue += f" (Thành công! +{reward})"
    elif reward < 0:
        dialogue += f" (Thất bại/Bị phạt {reward})"
        
    return dialogue

def interactive_mode():
    print("="*60)
    print(" 🤖 GIAO TIẾP VỚI DORY (Trí thông minh nhận thức)")
    print("="*60)
    print("Lệnh có sẵn:")
    print(" - [Enter]    : Cho Dory tự hành động 1 bước")
    print(" - auto [số]  : Cho Dory tự chạy N bước (VD: auto 10)")
    print(" - shock      : Tạo thảm họa (trừ 50% tài nguyên của Dory)")
    print(" - gift       : Tặng Dory 50 tài nguyên")
    print(" - exit       : Kết thúc giao tiếp")
    print("="*60)

    # Khởi tạo thế giới
    config = load_constraint_set("default-v1")
    system = SystemPhysics(config)
    
    # Khởi tạo não bộ Dory
    genome = CognitiveGenome()
    genome.beta = 64.0  # Trí nhớ tốt
    dory = E019C_CognitiveActor(seed=42, genome=genome)
    
    state = system.get_initial_state()
    tick = 0
    work_reward = 10.0
    auto_steps = 0
    
    while True:
        if auto_steps > 0:
            user_input = ""
            auto_steps -= 1
            time.sleep(0.1) # Chạy chậm lại để dễ nhìn
        else:
            user_input = input("\nBạn > ").strip().lower()

        if user_input == "exit" or user_input == "quit":
            print("Tạm biệt Dory!")
            break
        elif user_input.startswith("auto"):
            try:
                auto_steps = int(user_input.split()[1])
            except:
                print("Lệnh sai. Vui lòng nhập: auto [số]")
            continue
        elif user_input == "shock":
            state["resource"] *= 0.5
            print(f"\n⚡ THẦN LINH (Bạn) GIÁNG HOẠ! Năng lượng Dory bị giảm một nửa!")
            continue
        elif user_input == "gift":
            state["resource"] += 50
            print(f"\n🎁 THẦN LINH (Bạn) BAN PHƯỚC! Dory nhận được 50 năng lượng!")
            continue

        # Dory suy nghĩ và hành động
        tick += 1
        state = system.system_tick(state)
        
        if system.is_terminal(state):
            print("\n💀 Dory đã cạn kiệt năng lượng và gục ngã...")
            break
            
        obs = system.system_observe(state, tick)
        decision = dory.choose(obs)
        is_valid, _ = system.system_validate(state, decision)
        
        if is_valid:
            state = system.system_apply(state, decision)
            
        reward = -1.0 if not is_valid else (work_reward if decision == "work" else 0.0)
        
        # Dory học từ kết quả
        dory.update(str(obs), decision, reward, str(system.system_observe(state, tick)))
        
        # Dory phát biểu
        print(dory_speak(state, decision, reward))

if __name__ == "__main__":
    interactive_mode()
