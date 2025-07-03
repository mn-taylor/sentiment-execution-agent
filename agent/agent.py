from abc import ABC, abstractmethod
import numpy as np
import torch.nn as nn
import torch


class PolicyNetwork(nn.Module):
    def __init__(self, obv_dim, n_actions, hidden_dim=128):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(obv_dim, hidden_dim),
            nn.ReLU(True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(True),
            nn.Linear(hidden_dim, n_actions)
        )

    def forward(self, obv):
        return self.model(obv)
    
    
    def select_action(self, obv):
        logits = self.forward(obv)
        dist = torch.distributions.Categorical(logits=logits)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob

