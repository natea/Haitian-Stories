package org.ourstories.controllers
{
    import flash.events.ErrorEvent;
    import flash.events.Event;
    
    import mx.collections.ArrayCollection;
    
    import org.ourstories.models.FlvModel;
    import org.ourstories.services.IFlvService;
    import org.ourstories.services.Operation;
    
    public class Controller implements IController
    {
        
        [Bindable]
        public function set message(value:String):void
        {
            trace("set message "+value);
            _message = value;
        }
        public function get message():String
        {
            return _message;
        }
        private var _message:String;
        
        
        public function set flvService(value:IFlvService):void
        {
            _flvService = value;
        }
        public function get flvService():IFlvService
        {
            return _flvService;
        }
        private var _flvService:IFlvService;
        
        private var _activeOperations:ArrayCollection = new ArrayCollection();
        
        
        // controller actions
        // call service, which returns an operation
        
        public function ping():FlvModel
        {
            var flvModel:FlvModel = new FlvModel();
            performOperation(flvService.ping(flvModel));
            return flvModel;
        }
        public function getId():FlvModel
        {
            // creates an FlvModel with bindable id
            // calls service, performs operation
            // the bindable id will be populated on success
            var flvModel:FlvModel = new FlvModel();
            performOperation(flvService.getId(flvModel));
            return flvModel;
        }
        public function getIdSig():FlvModel
        {
            // creates an FlvModel with bindable id
            // calls service, performs operation
            // the bindable id will be populated on success
            var flvModel:FlvModel = new FlvModel();
            performOperation(flvService.getIdSig(flvModel));
            return flvModel;
        }
        public function setStatus(flvModel:FlvModel):FlvModel
        {
            performOperation(flvService.setStatus(flvModel));
            return flvModel;
        }
        public function setStatusType(flvModel:FlvModel):FlvModel
        {
            performOperation(flvService.setStatusType(flvModel));
            return flvModel;
        }
        public function linkFlvToStory(flvModel:FlvModel):FlvModel
        {
            performOperation(flvService.linkFlvToStory(flvModel));
            return flvModel;
        }
        public function dtrace(flvModel:FlvModel):FlvModel
        {
            if (OurStoriesConfig.DEBUG)
            {
                performOperation(flvService.dtrace(flvModel));
            }
            return flvModel;
        }
                
        
        private function performOperation(operation:Operation):void
        {
            if (_activeOperations.length == 0)
            {
                message = operation.message;
            }
            _activeOperations.addItem(operation);
            
            // setup listeners
            operation.addEventListener(ErrorEvent.ERROR, onOperationFail);
            operation.addEventListener(Event.COMPLETE, onOperationSuccess);
            // now execute command operation
            operation.execute();
            
        }
        
        private function onOperationFail(event:ErrorEvent):void
        {
            message = event.text;
            onOperationSuccess(event);
        }
        
        private function onOperationSuccess(event:Event):void
        {
            // remove operation from _activeOperations
            var index:int = _activeOperations.getItemIndex(event.target);
            if (index >= 0)
            {
                _activeOperations.removeItemAt(index);
                if (index == 0)
                {
                    message = (_activeOperations.length == 0) ? "" : 
                       Operation(_activeOperations.getItemAt(0)).message;
                }
            }
            
        }
        
        
    }
}