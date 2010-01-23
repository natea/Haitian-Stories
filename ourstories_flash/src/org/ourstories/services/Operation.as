package org.ourstories.services
{
    import flash.events.ErrorEvent;
    import flash.events.Event;
    import flash.events.EventDispatcher;
    
    import mx.controls.Alert;

    [Event(name="complete",type="flash.events.Event")]
    [Event(name="error",type="flash.events.ErrorEvent")]
        
    /**
     * Operation based on Joe Berkovitz MVCS.
     */
    public class Operation extends EventDispatcher
    {
        public function Operation()
        {
            
        }
        
        [Bindable]
        /**
         * Bindable status message to display to end user.
         */
        public var message:String;
        
        /**
         * Execute command, override.
         */
        public function execute():void
        {
            // override
        }
        
        /**
         * Handles operation success.
         */
        protected function onSuccess(event:Event):void
        {
            dispatchEvent(new Event(Event.COMPLETE));
        }

        /**
         * Handles operation fail.
         */
        protected function onFail(event:Event, 
            endUserMessage:String=""):void
        {
            if (endUserMessage != "")
            {
                Alert.show(endUserMessage, "Error");
            }
            var errorEvent:ErrorEvent = new ErrorEvent(ErrorEvent.ERROR);
            errorEvent.text = endUserMessage;
            dispatchEvent(errorEvent);
        }
        

    }
}