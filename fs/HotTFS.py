import config
from fs.TFS import TFS,TFSFileStateMachine,TFSFileMeta


class HotTFS(TFS):
    def __init__(self):
        # for i in range(block_numbers):
        #     open(os.path.join(path, '{:03x}'.format(i)), 'ab').close()
        self.bitmap = [TFS.FREE] * config.block_numbers
        self.counter = [0] * (config.block_numbers // config.chunk_length)
        self.file_list = {}
        self.overwritten = 0

    def allocate_blocks(self, blocks, lm_fn):
        cnt = 0
        offset = 0
        for pos in range(config.block_numbers):
            if lm_fn(self.bitmap[pos]):
                if offset == -1:
                    offset = pos
                cnt += 1
                if cnt >= blocks:
                    for blockIndex in range(offset, offset + blocks):
                        self.counter[ blockIndex // config.chunk_length ] += 1
                    return offset
            else:
                offset = -1
                cnt = 0
        raise LookupError
    def allocate_contrib_blocks(self, blocks, lm_fn):
        sortedChuncks = [{'num':item,'offset':index*config.chunk_length} for index, item in enumerate(self.counter) ]
        sortedChuncks.sort(key=lambda i:i['num'])
        for chunck in sortedChuncks:
            cnt = 0
            offset = chunck['offset']
            for pos in range(chunck['offset'], min(chunck['offset'] + config.chunk_length + blocks, config.block_numbers)):
                if lm_fn(self.bitmap[pos]):
                    if offset == -1:
                        offset = pos
                    cnt += 1
                    if cnt >= blocks:
                        return offset
                else:
                    offset = -1
                    cnt = 0
        print('error')
        raise LookupError

    def allocate_transparent_file_block(self, blocks):
        return self.allocate_contrib_blocks(blocks, lambda s: s == TFS.FREE)

if __name__ == '__main__':
    tfs = HotTFS()
    tfs.add_normal_file('a', 10)
    tfs.view_top_n_status(50)
    tfs.add_contrib_file('_b', 10)
    tfs.view_top_n_status(50)
    tfs.add_contrib_file('_b', 10)
    tfs.view_top_n_status(50)
    tfs.add_normal_file('c', 3)
    tfs.stat_normal_file('c')
    tfs.view_top_n_status(50)
    tfs.delete_normal_file('c')
    tfs.stat_normal_file('a')
    tfs.view_top_n_status(50)
    tfs.stat_contrib_file('_b')
    tfs.view_top_n_status(50)
