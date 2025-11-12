"""
Agent2가 제대로 반영되는지 확인하는 테스트 스크립트
"""
import numpy as np
from data_processor import DataProcessor
from environment import MARLStockEnv
from config import N_AGENTS, WINDOW_SIZE

def test_agent2_features():
    print("=" * 60)
    print("Agent2 피처 반영 테스트")
    print("=" * 60)
    
    # 1. 데이터 로드
    print("\n[1] 데이터 처리 중...")
    processor = DataProcessor()
    (features_unnormalized_df, prices_df, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols) = processor.process()
    
    print(f"\n✓ Agent 0 피처 ({len(agent_0_cols)}개): {agent_0_cols}")
    print(f"✓ Agent 1 피처 ({len(agent_1_cols)}개): {agent_1_cols}")
    print(f"✓ Agent 2 피처 ({len(agent_2_cols)}개): {agent_2_cols}")
    
    # 2. 정규화
    split_idx = int(len(features_unnormalized_df) * 0.8)
    train_features_unnorm = features_unnormalized_df.iloc[:split_idx]
    train_prices = prices_df.iloc[:split_idx]
    
    train_features, _ = processor.normalize_data(train_features_unnorm, train_features_unnorm)
    
    # 3. 환경 생성
    print("\n[2] 환경 생성 중...")
    env = MARLStockEnv(
        train_features, train_prices,
        agent_0_cols, agent_1_cols, agent_2_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    print(f"\n✓ Agent 0 관측 차원: {env.observation_dim_0}")
    print(f"✓ Agent 1 관측 차원: {env.observation_dim_1}")
    print(f"✓ Agent 2 관측 차원: {env.observation_dim_2}")
    
    # 4. 환경 리셋 및 관측값 확인
    print("\n[3] 환경 리셋 및 관측값 확인...")
    obs_dict, info = env.reset()
    
    print(f"\n✓ Agent 0 관측값 shape: {obs_dict['agent_0'].shape}")
    print(f"✓ Agent 1 관측값 shape: {obs_dict['agent_1'].shape}")
    print(f"✓ Agent 2 관측값 shape: {obs_dict['agent_2'].shape}")
    
    # 5. 각 에이전트가 받는 실제 피처 데이터 확인
    print("\n[4] 각 에이전트의 실제 피처 데이터 샘플 (첫 5개 값):")
    
    # 포트폴리오 상태 제외하고 순수 피처만 추출
    obs_0_features = obs_dict['agent_0'][:-2]  # 마지막 2개는 포트폴리오 상태
    obs_1_features = obs_dict['agent_1'][:-2]
    obs_2_features = obs_dict['agent_2'][:-2]
    
    print(f"\n  Agent 0 피처 데이터 (처음 5개): {obs_0_features[:5]}")
    print(f"  Agent 1 피처 데이터 (처음 5개): {obs_1_features[:5]}")
    print(f"  Agent 2 피처 데이터 (처음 5개): {obs_2_features[:5]}")
    
    # 6. 세 에이전트의 피처가 서로 다른지 확인
    print("\n[5] 에이전트 간 피처 차이 검증:")
    
    # 각 에이전트의 피처 길이가 다르므로, 길이 자체가 다르면 다른 것으로 판단
    len_0 = len(obs_0_features)
    len_1 = len(obs_1_features)
    len_2 = len(obs_2_features)
    
    print(f"\n  Agent 0 피처 길이: {len_0}")
    print(f"  Agent 1 피처 길이: {len_1}")
    print(f"  Agent 2 피처 길이: {len_2}")
    
    diff_0_1 = (len_0 != len_1)
    diff_0_2 = (len_0 != len_2)
    diff_1_2 = (len_1 != len_2)
    
    print(f"\n  Agent 0 vs Agent 1 다름: {diff_0_1} {'✓' if diff_0_1 else '✗'}")
    print(f"  Agent 0 vs Agent 2 다름: {diff_0_2} {'✓' if diff_0_2 else '✗'}")
    print(f"  Agent 1 vs Agent 2 다름: {diff_1_2} {'✓' if diff_1_2 else '✗'}")
    
    # 7. Agent 2 전용 피처 확인 (VIX가 포함되어 있는지)
    print("\n[6] Agent 2 전용 피처 확인:")
    
    # Agent 2의 피처 목록에 VIX가 있는지 확인
    has_vix = 'VIX' in agent_2_cols
    print(f"\n  Agent 2가 VIX 피처를 가지고 있음: {has_vix} {'✓' if has_vix else '✗'}")
    
    # 실제 데이터에서 VIX 값이 0이 아닌지 확인
    vix_idx = agent_2_cols.index('VIX') if has_vix else -1
    if vix_idx >= 0:
        # window_size * n_features 형태로 저장되므로
        vix_values = obs_2_features[vix_idx::env.n_features_agent_2]
        print(f"  Agent 2의 VIX 값 샘플 (최근 5개): {vix_values[-5:]}")
        print(f"  VIX 값이 0이 아님: {not np.allclose(vix_values, 0)} {'✓' if not np.allclose(vix_values, 0) else '✗'}")
    
    # 8. 한 스텝 진행 후에도 Agent 2가 제대로 작동하는지 확인
    print("\n[7] 한 스텝 진행 후 Agent 2 동작 확인...")
    
    actions = {f'agent_{i}': 1 for i in range(N_AGENTS)}  # 모두 Hold
    next_obs, rewards, dones, _, info = env.step(actions)
    
    print(f"\n  Agent 2 보상: {rewards['agent_2']:.4f}")
    print(f"  Agent 2 다음 관측값 shape: {next_obs['agent_2'].shape}")
    
    # 9. 최종 결과
    print("\n" + "=" * 60)
    all_checks_passed = (
        diff_0_1 and diff_0_2 and diff_1_2 and 
        has_vix and 
        env.observation_dim_2 == WINDOW_SIZE * env.n_features_agent_2 + 2
    )
    
    if all_checks_passed:
        print("✓ 모든 테스트 통과! Agent 2가 제대로 반영되고 있습니다.")
    else:
        print("✗ 일부 테스트 실패. Agent 2 설정을 다시 확인하세요.")
    print("=" * 60)
    
    return all_checks_passed

if __name__ == "__main__":
    test_agent2_features()
