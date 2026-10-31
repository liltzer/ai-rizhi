import gzip,io,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from core import Store,Updater,FeedFetcher,now
class CollectorTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/'test.sqlite3')
 def tearDown(self):self.tmp.cleanup()
 def feed(self,url):return ('<rss><channel><item><title>Example</title><link>https://example.org/a?utm_source=rss</link><pubDate>'+now().strftime('%a, %d %b %Y %H:%M:%S %z')+'</pubDate><description>Summary</description></item></channel></rss>').encode()
 def test_roundtrip_dedup_and_failure(self):
  sources=[{'name':'Test','url':'https://example.org/rss'}];u=Updater(self.store,sources,FeedFetcher(self.feed));self.assertEqual(u.run()['added'],1);self.assertEqual(u.run()['added'],0)
  backup=self.store.export();new=Store(Path(self.tmp.name)/'new.sqlite3');new.import_backup(backup);self.assertEqual(len(new.articles()),1)
  success=self.store.get('lastSuccessfulAt');u.fetcher=FeedFetcher(lambda url:(_ for _ in ()).throw(TimeoutError()));self.assertEqual(u.run()['status'],'failed');self.assertEqual(self.store.get('lastSuccessfulAt'),success);self.assertEqual(len(self.store.articles()),1)
 def test_private_state_excluded(self):
  self.store.set('admin',{'password':'test-not-real'});self.assertNotIn('admin',self.store.export())
 def test_future_unknown_unsafe_ignored(self):
  data=b'<rss><channel><item><title>No date</title><link>https://example.org/a</link></item><item><title>Unsafe</title><link>javascript:alert(1)</link><pubDate>Fri, 30 Oct 2026 08:00:00 GMT</pubDate></item></channel></rss>'
  self.assertEqual(FeedFetcher(lambda url:data).fetch({'name':'Test','url':'https://example.org/rss'}),[])
 def test_gzip_feed_preserves_articles(self):
  source={'name':'Test','url':'https://example.org/rss'}
  plain=FeedFetcher(self.feed).fetch(source)
  compressed=FeedFetcher(lambda url:gzip.compress(self.feed(url))).fetch(source)
  self.assertEqual([(a['id'],a['title'],a['summary']) for a in plain],[(a['id'],a['title'],a['summary']) for a in compressed])
 def test_gzip_expanded_size_is_bounded(self):
  data=gzip.compress(b'a'*(6*1024*1024+1))
  with self.assertRaisesRegex(ValueError,'来源内容过大'):
   FeedFetcher(lambda url:data).fetch({'name':'Test','url':'https://example.org/rss'})
if __name__=='__main__':unittest.main()
