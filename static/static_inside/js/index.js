/* eslint-disable */
// eslint-disable-next-line
import React , { Component, PropTypes }from 'react'
import { render } from 'react-dom'
import { createStore, combineReducers, applyMiddleware,compose} from 'redux'
import createHistory from 'history/createBrowserHistory'
import {Switch, Route ,Redirect} from 'react-router'
import { Provider } from 'react-redux'
import { ConnectedRouter, routerReducer, routerMiddleware, push } from 'react-router-redux'
import reducers from './reducers'
import promiseXHR from './funStore/ServerFun'
import AuthProvider from './funStore/AuthProvider'
import SaasNaviBar from './components/SaasNaviBar'
import Login from './containers/Login'
import Register from './containers/Register'
import GMScope from './containers/GMScope'
import CWScope from './containers/CWScope'
import GHWScope from './containers/GHWScope'
import GCScope from './containers/GCScope'
import GDScope from './containers/GDScope'
import GAScope from './containers/GAScope'
import MTScope from './containers/MTScope'
import JMScope from './containers/JMScope'
import JRScope from './containers/JRScope'
import ECScope from './containers/ECScope'
import BGScope from './containers/BGScope'
import QRScope from './containers/QRScope'
import UMScope from './containers/UMScope'
import UCScope from './containers/UCScope'
import TMScope from './containers/TMScope'
import PCScope from './containers/PCScope'
import RMScope from './containers/RMScope'
import GIScope from './containers/GIScope'
import NRScope from './containers/NRScope'
import SysScope from './containers/SysScope'
import SetScope from './containers/SetScope'
import InitScope from './containers/InitScope'
import KYScope from './containers/KYScope'
import LoginAgain from './containers/LoginAgain'
import Test from './containers/Test'
import Home from './containers/Home'
import Error from './containers/Error'
import SMScope from './containers/SMScope'
import NeedOwnScope from './containers/NeedOwnScope'
import GAMScope from './containers/GAMScope'
import {API_PATH} from './constants/OriginName'
import WebSocketConnect from './funStore/WebSocketConnect'
// 控制台：window.debugger = function(...ar){console.log(...ar)}
window.debugger = (...ar) => {
  // 如果想看log的话重写恢复下面代码
  // console.log(...ar)
}
/* global location */
/* eslint no-restricted-globals: ["off", "location"] */
const history = createHistory({basename: ''})
// Build the middleware for intercepting and dispatching navigation actions
const middleware = routerMiddleware(history)
// Add the reducer to your store on the `router` key
// Also apply our middleware for navigating
export const store = createStore(
  reducers,
  applyMiddleware(middleware),
  // compose(applyMiddleware(middleware),window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()) //插件调试，未安装会报错
)
const pullUserinfo = (url,resolve) => (
       promiseXHR(url,{type:'Bearer',value:resolve},null,'GET')
        .then((res) => {
          const data = eval('('+res+')')
          return data.resultContent
        })
)

const MarketScope = ({location}) => {
  if(location.pathname=='/'){
    window.location.href = window.location.origin + '/marketPortal'
  }
  return(
    <div>
      {location.pathname=='/' ?
        '' : <Route  component={Login} />
      }
    </div>
  )
}

const MainScope = ({location})=>{
  const init = location.pathname == "/InitScope"
  const judge = location.pathname == "/GMScope"
  ||location.pathname == "/Home"
  ||location.pathname == "/CWScope"
  ||location.pathname == "/GCScope"
  ||location.pathname == "/GDScope/GHWScope"
  ||location.pathname == "/GDScope"
  ||location.pathname == "/MTScope"
  ||location.pathname == "/JMScope"
  ||location.pathname == "/JRScope"
  ||location.pathname == "/ECScope"
  ||location.pathname == "/GAScope"
  ||location.pathname == "/BGScope"
  ||location.pathname == "/QRScope"
  ||location.pathname == "/UMScope"
  ||location.pathname == "/TMScope/UCScope"
  ||location.pathname == "/TMScope"
  ||location.pathname == "/PCScope"
  ||location.pathname == "/RMScope"
  ||location.pathname == "/GIScope"
  ||location.pathname == "/NRScope"
  ||location.pathname == "/NRScope/table"
  ||location.pathname == "/NRScope/build"
  ||location.pathname == "/NRScope/edit"
  ||location.pathname == "/SysScope"
  ||location.pathname == "/IMScope"
  ||location.pathname == "/HomeScope"
  ||location.pathname == "/KYScope"
  ||location.pathname == "/NeedOwnScope"
  ||location.pathname == "/GAMScope"
  if(judge||init){
   const userInfo = store.getState().userInfo
   AuthProvider.encodeClientId()
      AuthProvider.getAccessToken()
      .then((resolve,reject) => {
        if(store.getState().userInfo.info.userinfo!=undefined){
          return {data: new Promise((resolve,reject)=>{
            resolve(store.getState().userInfo.info)
          }),
           token:resolve}
        }else {
          return {data: pullUserinfo(API_PATH+'/tenantadmin/authsec/tenantbase/currentuser',resolve),
           token:resolve}
        }
      })
      .then((resolve,reject) => {
        resolve.data.then((res) => {
          if(store.getState().userInfo.info.userinfo==undefined){
             store.dispatch(
              {type: 'USERINFO_INIT' ,data: res}
            )
            return 'DONE'
          }else {
            return 'EXIST'
          }
        })
        .then(res => {
          if(location.pathname!='/login'&&location.pathname!='/'&&location.pathname!='/offline'){
            if(store.getState().socketState.webSocket==''){
                 store.dispatch(
                   {type: 'SET_SOCKET' ,socket: new WebSocketConnect()}
                 )
            }
          }else{
            if(store.getState().socketState.webSocket!=''){
              store.getState().socketState.webSocket.state.socket.close()
            }
          }
        })
       return {token: resolve.token, promiseData: resolve.data}
      })
      .then((resolve) => {
        if(store.getState().naviMetaData.naviList.length==0||store.getState().socketState.webSocket==''){
          resolve.promiseData
          .then((res) => {
            const array = res.userinfo.roles
            const formData = array.map(item => ({id:item.id}))
            const url = API_PATH+'/basis-api/authsec/menu/tree/roles'
            promiseXHR(url,{type:'Bearer',value:resolve.token},formData,'POST')
            .then((res) =>{
              const data = eval('('+res+')')
              return store.dispatch(
                {type: 'NAVILIST_INIT' ,data: data.resultContent}
              )
            })
          })
        }else {
          return
        }
      })
    }
  return(
    <div className="saas-container" >
      {judge&&!init? <SaasNaviBar location = {location.pathname} /> : ''}
      <Switch>
        <Route  path="/InitScope" component={InitScope} />
        <Route  path="/Home"    component={Home}    />
        <Route  path="/GMScope" component={GMScope} />
        <Route  path="/CWScope" component={CWScope} />
        <Route  path="/GCScope" component={GCScope} />
        <Route  path="/GDScope/GHWScope"component={GHWScope}/>
        <Route  path="/GDScope" component={GDScope} />
        <Route  path="/MTScope" component={MTScope} />
        <Route  path="/JMScope" component={JMScope} />
        <Route  path="/JRScope" component={JRScope} />
        <Route  path="/ECScope" component={ECScope} />
        <Route  path="/GAScope" component={GAScope} />
        <Route  path="/BGScope" component={BGScope} />
        <Route  path="/QRScope" component={QRScope} />
        <Route  path="/UMScope" component={UMScope} />
        <Route  path="/TMScope/UCScope" component={UCScope} />
        <Route  path="/TMScope" component={TMScope} />
        <Route  path="/PCScope" component={PCScope} />
        <Route  path="/RMScope" component={RMScope} />
        <Route  path="/GIScope" component={GIScope} />
        <Route  path="/NRScope" component={NRScope} />
        <Route  path="/KYScope" component={KYScope} />
        <Route  path="/SysScope" component={SysScope} />
        <Route  path="/IMScope" component={SetScope} />
        <Route  path="/offline" component={LoginAgain} />
        <Route  path="/register" component={Register} />
        <Route  path="/NeedOwnScope" component={NeedOwnScope} />
        <Route  path="/GAMScope" component={GAMScope} />
        <Route  path="/" component = {MarketScope} />
        <Route  component={Error} />
      </Switch>
    </div>
  )
}
render(
  <Provider store={store}>
     { /* ConnectedRouter will use the store from Provider automatically */ }
     <ConnectedRouter history={history}>
       <div>
         <Switch>
           <Route exact path="/login" component={Login} />
           <Route  path="/" component = {MainScope} />
           <Route  component={Error} />
         </Switch>
       </div>
     </ConnectedRouter>
   </Provider>,
  document.getElementById('root')
)



// WEBPACK FOOTER //
// ./src/index.js