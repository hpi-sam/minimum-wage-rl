# # =============== Continous Actor Critic =====================

# def a2c_continuous(**kwargs):
#     generate_tag(kwargs)
#     kwargs.setdefault('log_level', 0)
#     config = Config()
#     config.merge(kwargs)

#     config.num_workers = 16
#     config.task_fn = lambda: Task(config.game, num_envs=config.num_workers)
#     config.eval_env = Task(config.game)
#     config.optimizer_fn = lambda params: torch.optim.RMSprop(params, lr=0.0007)
#     config.network_fn = lambda: GaussianActorCriticNet(
#         config.state_dim, config.action_dim,
#         actor_body=FCBody(config.state_dim), critic_body=FCBody(config.state_dim))
#     config.discount = 0.99
#     config.use_gae = True
#     config.gae_tau = 1.0
#     config.entropy_weight = 0.01
#     config.rollout_length = 5
#     config.gradient_clip = 5
#     config.max_steps = int(2e7)
#     run_steps(A2CAgent(config))
