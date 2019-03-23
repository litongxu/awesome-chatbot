#!/usr/bin/python3.6

# coding=utf-8
# Copyright 2019 The Tensor2Tensor Authors.
#
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

"""Query an exported model. Py2 only. Install tensorflow-serving-api."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
sys.path.append('..')
from oauth2client.client import GoogleCredentials
from six.moves import input  # pylint: disable=redefined-builtin

from tensor2tensor import problems as problems_lib  # pylint: disable=unused-import
from tensor2tensor.serving import serving_utils
from tensor2tensor.utils import registry
from tensor2tensor.utils import usr_dir
from tensor2tensor.utils.hparam import HParams
import tensorflow as tf
from model.settings import hparams
import functools

flags = tf.flags
FLAGS = flags.FLAGS

flags.DEFINE_string("server", 'localhost:9001', "Address to Tensorflow Serving server.")
flags.DEFINE_string("servable_name", 'chat_line_problem', "Name of served model.")
flags.DEFINE_string("problem", 'chat_line_problem', "Problem name.")
flags.DEFINE_string("data_dir", hparams['data_dir'] + '/t2t_data/', "Data directory, for vocab files.")
flags.DEFINE_string("t2t_usr_dir", None, "Usr dir for registrations.")
flags.DEFINE_string("inputs_once", None, "Query once with this input.")
flags.DEFINE_integer("timeout_secs", 10, "Timeout for query.")

# For Cloud ML Engine predictions.
flags.DEFINE_string("cloud_mlengine_model_name", None,
                    "Name of model deployed on Cloud ML Engine.")
flags.DEFINE_string(
    "cloud_mlengine_model_version", None,
    "Version of the model to use. If None, requests will be "
    "sent to the default version.")

def lazy_property( function):
    attribute = '_cache_' + function.__name__

    @property
    @functools.wraps(function)
    def decorator(self):
        if not hasattr(self, attribute):
            setattr(self, attribute, function(self))
        return getattr(self, attribute)

    return decorator


class Request:
    def __init__(self, argv):
        global flags

        self.request_fn = None
        self.problem = None
        self.args = argv
        #self.set_flags()

        #tf.app.run(main=self.main, argv=argv)
        self.main()

    @lazy_property
    def validate_flags(self):
        """Validates flags are set to acceptable values."""
        global FLAGS
        if FLAGS.cloud_mlengine_model_name and False:
            assert not FLAGS.server
            assert not FLAGS.servable_name
        else:
            assert FLAGS.server
            assert FLAGS.servable_name

    @lazy_property
    def make_request_fn(self):
        """Returns a request function."""
        global FLAGS
        if FLAGS.cloud_mlengine_model_name:
            request_fn = serving_utils.make_cloud_mlengine_request_fn(
                credentials=GoogleCredentials.get_application_default(),
                model_name=FLAGS.cloud_mlengine_model_name,
                version=FLAGS.cloud_mlengine_model_version)
        else:

            request_fn = serving_utils.make_grpc_request_fn(
                servable_name=FLAGS.servable_name,
                server=FLAGS.server,
                timeout_secs=FLAGS.timeout_secs)
        return request_fn

    @lazy_property
    def main(self):
        global FLAGS, flags
        print('here 3')
        #self.set_flags()

        tf.logging.set_verbosity(tf.logging.INFO)
        self.validate_flags()
        print(FLAGS.data_dir)
        usr_dir.import_usr_dir(FLAGS.t2t_usr_dir)
        self.problem = registry.problem(FLAGS.problem)
        hparams = HParams(
            data_dir=os.path.expanduser(FLAGS.data_dir))
        self.problem.get_hparams(hparams)
        self.request_fn = self.make_request_fn()
        while False:
            self.request(self.problem, self.request_fn)
            pass

    @lazy_property
    def request(self, problem, request_fn, input_line=None):
        global FLAGS, flags
        print(input_line)
        if input_line is None:
            inputs = FLAGS.inputs_once if FLAGS.inputs_once else input(">> ")
        else:
            inputs = input_line
        outputs = serving_utils.predict([inputs], problem, request_fn)
        outputs, = outputs
        output, score = outputs
        if input_line is not None:
            return output

        if len(score.shape) > 0:  # pylint: disable=g-explicit-length-test
            print_str = """
Input:
{inputs}
    
Output (Scores [{score}]):
{output}
        """
            score_text = ",".join(["{:.3f}".format(s) for s in score])
            print(print_str.format(inputs=inputs, output=output, score=score_text))
        else:
            print_str = """
Input:
{inputs}
    
Output (Score {score:.3f}):
{output}
        """
            print(print_str.format(inputs=inputs, output=output, score=score))

        if FLAGS.inputs_once:
            return

    @lazy_property
    def set_flags(self):

        global flags, FLAGS

        for i in self.args:
            if i is not None and i.startswith('--'):
                ii = i[2:]
                #print(ii)
                z = ii.split('=')[-1]
                i = ii.split('=')[0]
                print(i, z,'<:')
                flags.FLAGS.set_default(i, z)





if __name__ == "__main__":
    flags.mark_flags_as_required(["problem", "data_dir"])

    q = Request(argv=sys.argv)

    #tf.app.run(main=q.main, argv=sys.argv)
