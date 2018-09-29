import my_logger
import result_write

log = my_logger.get_logger(log_file_name='test.log')
log.info('test')

test_head = ['year', 'str']
test_body = [[2008, 'asd'], [2009, 'as1']]

result_write.write_csv('test.csv', header=test_head, body_list=test_body)
