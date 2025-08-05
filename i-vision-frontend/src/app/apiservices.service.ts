import { DOCUMENT } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { inject, Inject, Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { error } from 'console';
import { catchError, finalize } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiservicesService {

  constructor(private http:HttpClient,  @Inject(DOCUMENT) private document: Document) { }

  private _snackBar = inject(MatSnackBar);
    
  openSnackBar() {
    this._snackBar.open("Oops! Something went wrong. Please try again.", "X", {duration: 10000});
  }

  url = 'http://localhost:8000/';
  // url = 'http://192.168.181.141:8000/';

  getCutouts(image:any, category:any){

    this.document.getElementById("loading-overlay")?.classList.add('active')


    const formData = new FormData();
    formData.append('raw_image', image);
    formData.append('category', category);

    return this.http.post(`${this.url}get/objects/`, formData).pipe(
      catchError(err => {
        this.openSnackBar()
        throw err
      }),
      finalize(()=>{this.document.getElementById("loading-overlay")?.classList.remove('active')})
    );
  }

  addImage(data:any){
    this.document.getElementById("loading-overlay")?.classList.add('active')

    return this.http.post(`${this.url}add/image/`, data).pipe(
      catchError(err => {
        this.openSnackBar()
        throw err
      }),
      finalize(()=>{this.document.getElementById("loading-overlay")?.classList.remove('active')})
    );
  }

  searchImage(query:any){

    this.document.getElementById("loading-overlay")?.classList.add('active')

    return this.http.post(`${this.url}search/img/`, query).pipe(
      catchError(err => {
        this.openSnackBar()
        throw err
      }),
      finalize(()=>{this.document.getElementById("loading-overlay")?.classList.remove('active')})
    );
  }

  
}
