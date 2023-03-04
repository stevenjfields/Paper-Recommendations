import * as React from 'react';
import SearchInterface from './SearchInterface';
import './SearchModal.css';

export default class SearchModal extends React.Component<SearchInterface, {}> {
    constructor (props: SearchInterface){
        super(props);
    }

    render() {
        if (this.props.isOpen) {
            return (
                <div className='SearchModal' onClick={this.props.toggle}>
                    <div className='content' onClick={e => e.stopPropagation()}>
                        <div className='title'>
                            <h4>Test Title</h4>
                        </div>
                        <div className='body'>
                            Random Stuff
                        </div>
                        <div className='footer'>
                            <button onClick={this.props.toggle} className='button'>Close</button>
                        </div>
                    </div>
                </div>
            );
        }
    }
}