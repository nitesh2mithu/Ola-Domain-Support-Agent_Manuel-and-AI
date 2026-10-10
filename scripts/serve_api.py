"""Run one offline worker on 127.0.0.1; Ctrl-C stops the local server."""
import argparse
from smoke_tests.runtime import prepare_runtime
prepare_runtime()
from api.offline import LocalhostAudit


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    LocalhostAudit(args.port).install()  # Before server/framework imports.
    import uvicorn
    from api.app import app
    uvicorn.run(app,host='127.0.0.1',port=args.port,workers=1,loop='asyncio',
                access_log=False,log_config=None)


if __name__=='__main__':main()
