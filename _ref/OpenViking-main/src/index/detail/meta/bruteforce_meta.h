// Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
// SPDX-License-Identifier: Apache-2.0
#pragma once
#include <string>
#include <memory>
#include "index/detail/meta/vector_index_meta.h"

namespace vectordb {

class BruteForceMeta : public VectorIndexMeta {};

using BruteForceMetaPtr = std::shared_ptr<BruteForceMeta>;

}  // namespace vectordb