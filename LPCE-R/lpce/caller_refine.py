import math
import torch
from lpce.utils import *

class Caller_RefineModule(object):

    def __init__(self, cuda, model, min_label, max_label, operat_dim, tb_dim, filter_dim, join_dim):
        super(Caller_RefineModule, self).__init__()
        self.cuda_use = cuda
        self.model = model
        self.min_label = min_label
        self.max_label = max_label
        self.norm_min_label = np.log(min_label)
        self.norm_max_label = np.log(max_label)
        self.operat_dim = operat_dim
        self.table_dim = tb_dim
        self.filter_dim = filter_dim
        self.join_dim = join_dim




    def testConnectLayer(self, feature, real_hidden, content_hidden, right_hidden):

        self.model.eval()
        feature = np.array(feature)
        operation_feat = feature[:, 0:self.operat_dim]
        table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
        filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
        join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]

        operation_feat = torch.from_numpy(operation_feat)
        table_feat = torch.from_numpy(table_feat)
        filter_feat = torch.from_numpy(filter_feat)
        join_feat = torch.from_numpy(join_feat)
        real_hidden = torch.from_numpy(np.array(real_hidden))
        content_hidden = torch.from_numpy(np.array(content_hidden))
        right_hidden = torch.from_numpy(np.array(right_hidden))

        operation_feat = operation_feat.float()
        table_feat = table_feat.float()
        filter_feat = filter_feat.float()
        join_feat = join_feat.float()
        real_hidden = real_hidden.float()
        content_hidden = content_hidden.float()
        right_hidden = right_hidden.float()

        estimate_output, c = self.model._connctLayer_call_postgre(
            operation_feat,
            table_feat,
            filter_feat,
            join_feat,
            real_hidden,
            content_hidden,
            right_hidden
        )

        estimate = estimate_output.data.numpy()
        output = []
        for i in range(len(estimate)):
            estimate[i] = estimate[i] * (self.norm_max_label - self.norm_min_label) + self.norm_min_label
            output.append(math.exp(estimate[i]))

        hidden = c.data.numpy()
        return output, hidden



    def testInternalLayer(self, feature, refine_hidden, right_hidden):
        self.model.eval()
        feature = np.array(feature)
        operation_feat = feature[:, 0:self.operat_dim]
        table_feat = feature[:, self.operat_dim : self.operat_dim + self.table_dim ]
        filter_feat = feature[:, self.operat_dim + self.table_dim : self.operat_dim + self.table_dim + self.filter_dim]
        join_feat = feature[:, self.operat_dim + self.table_dim + self.filter_dim : self.operat_dim + self.table_dim + self.filter_dim+self.join_dim]

        operation_feat = torch.from_numpy(operation_feat)
        table_feat = torch.from_numpy(table_feat)
        filter_feat = torch.from_numpy(filter_feat)
        join_feat = torch.from_numpy(join_feat)
        refine_hidden = torch.from_numpy(np.array(refine_hidden))
        right_hidden = torch.from_numpy(np.array(right_hidden))

        operation_feat = operation_feat.float()
        table_feat = table_feat.float()
        filter_feat = filter_feat.float()
        join_feat = join_feat.float()
        refine_hidden = refine_hidden.float()
        right_hidden = right_hidden.float()

        estimate_output, c = self.model._internalLayer_call_postgre(
            operation_feat,
            table_feat,
            filter_feat,
            join_feat,
            refine_hidden,
            right_hidden
        )

        estimate = estimate_output.data.numpy()
        output = []
        for i in range(len(estimate)):
            estimate[i] = estimate[i] * (self.norm_max_label - self.norm_min_label) + self.norm_min_label
            output.append(math.exp(estimate[i]))

        hidden = c.data.numpy()
        return output, hidden

