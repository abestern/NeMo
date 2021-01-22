# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase

import pytest
import pytorch_lightning as pl
from omegaconf import OmegaConf

import nemo.collections.nlp.models as models


def set_up_test(data_dir, model):
    trainer = pl.Trainer(gpus=[0])

    model.set_trainer(trainer)
    model.update_data_dir(data_dir)

    # TODO update the pre-trained model with the new config to remove setup_train_data
    test_ds = OmegaConf.create(
        {
            'text_file': 'text_dev.txt',
            'labels_file': 'labels_dev.txt',
            'shuffle': False,
            'num_samples': -1,
            'batch_size': 8,
        }
    )

    model._cfg.dataset.use_cache = False
    trainer.test(model)
    model.setup_test_data(test_data_config=test_ds)
    return trainer.test(model)[0]


class TestPretrainedModelPerformance(TestCase):
    @pytest.mark.unit
    def test_punct_capit_with_bert(self):
        data_dir = '/home/TestData/nlp/token_classification_punctuation/fisher'
        model = models.PunctuationCapitalizationModel.from_pretrained("Punctuation_Capitalization_with_BERT")

        metrics = set_up_test(data_dir, model)

        assert abs(metrics['punct_precision'] - 52.3024) < 0.001
        assert abs(metrics['punct_recall'] - 58.9220) < 0.001
        assert abs(metrics['punct_f1'] - 53.2976) < 0.001
        assert int(model.punct_class_report.total_examples) == 128

    @pytest.mark.unit
    def test_ner_model(self):
        data_dir = '/home/TestData/nlp/token_classification_punctuation/gmb'
        model = models.TokenClassificationModel.from_pretrained("NERModel")

        metrics = set_up_test(data_dir, model)

        assert abs(metrics['precision'] - 96.0937) < 0.001
        assert abs(metrics['recall'] - 96.0146) < 0.001
        assert abs(metrics['f1'] - 95.6076) < 0.001
        assert int(model.classification_report.total_examples) == 202
